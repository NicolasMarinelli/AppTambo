# Laboratorio

App para el personal de laboratorio del tambo: evalúa cultivos (mastitis,
estado de calostro, etc.) mandando la foto de la muestra + fotos de
referencia a un modelo de IA con visión (Claude), y deja que un
laboratorista confirme o corrija el veredicto antes de guardarlo como
definitivo.

**No tiene usuarios propios.** Reutiliza la tabla `users` de
[tambo](../tambo) — mismo login, mismo hash de contraseña, mismo esquema de
JWT — así que un usuario con rol `admin` o `laboratorio` en tambo puede
entrar acá sin crear una cuenta nueva, y un token emitido al loguearse en
una app sirve en la otra. Cualquier otro rol (ej. `operario`) recibe
"Acceso denegado", aunque la contraseña sea correcta.

## Stack

- Backend: FastAPI + SQLAlchemy + Alembic + JWT (idéntico a tambo)
- Frontend: React + Vite + TypeScript (mismos patrones/paleta que tambo)
- Base de datos: la misma base Postgres de tambo ("cami"), con un rol y un
  schema propios — ver "Cómo se conecta a la base" más abajo
- Fotos: Cloudinary (mismo proveedor que ya usa task-verifier)
- IA: Anthropic Claude con visión (mismo proveedor que ya usa
  task-verifier — ver `task-verifier/backend/app/services/ia_service.py`
  como referencia del patrón original)

## Cómo se conecta a la base de datos

A diferencia de task-verifier y tambo, laboratorio **no tiene una base de
datos propia**. Como no tiene usuarios propios, se conecta directamente a
la base de tambo ("cami") con un rol de Postgres separado que tiene:

- **Solo lectura (`SELECT`)** sobre las tablas de tambo en el schema
  `public` (hoy, solo `users`) — nunca hace `INSERT`/`UPDATE`/`DELETE` ahí.
  Ese permiso se otorga vía `ALTER DEFAULT PRIVILEGES`, así que también
  cubre automáticamente tablas que tambo cree más adelante, sin tocar nada
  acá.
- **Dueño exclusivo** de su propio schema `laboratorio` dentro de esa misma
  base, donde viven sus propias tablas (`tipos_analisis`,
  `fotos_referencia`, `resultados_laboratorio`).

Este rol y este schema los crea `infra/postgres-init/init-multiple-dbs.sh`
(en la raíz del repo) la primera vez que se levanta el volumen de Postgres.
Las migraciones de Alembic de laboratorio (`alembic/env.py`) están
restringidas por diseño al schema `laboratorio` — nunca generan ni aplican
DDL sobre `public.users`, aunque esa tabla comparta el mismo `Base` de
SQLAlchemy.

**¿Por qué compartir la base en vez de una API entre servicios?** Porque
hoy no existe ningún mecanismo de comunicación entre las apps de este
repo — cada una tiene su propia base aislada y su propia auth (ver
`../README.md`, sección "Estado de la integración"). Construir un contrato
de API interno nuevo solo para esto era más trabajo y más superficie de
fallo que usar el hecho de que ya comparten el mismo proceso de Postgres.
La misma razón aplica para `resultados_laboratorio`: vive en esa base para
que tambo pueda leerla en el futuro con un simple `JOIN`, sin necesidad de
ningún endpoint intermedio.

### Si ya tenés el volumen de Postgres corriendo desde antes

`init-multiple-dbs.sh` solo corre la primera vez que se crea el volumen
(comportamiento estándar de la imagen de Postgres). Si ya tenías
`task-verifier`/`tambo` corriendo antes de que existiera `laboratorio`, hay
que aplicar el mismo SQL a mano, una sola vez, contra el Postgres ya
levantado (no destructivo — no toca datos existentes):

```bash
docker exec -it appcami_db psql -U postgres -d postgres -c "
    CREATE USER laboratorio WITH PASSWORD 'laboratorio';
    GRANT CONNECT ON DATABASE cami TO laboratorio;
"
docker exec -it appcami_db psql -U postgres -d cami -c "
    GRANT USAGE ON SCHEMA public TO laboratorio;
    ALTER DEFAULT PRIVILEGES FOR ROLE cami IN SCHEMA public GRANT SELECT ON TABLES TO laboratorio;
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO laboratorio;
    CREATE SCHEMA IF NOT EXISTS laboratorio AUTHORIZATION laboratorio;
"
```

(Ajustá el password si en tu `.env` de raíz pusiste otro valor para
`LABORATORIO_DB_PASSWORD`.)

## Puesta en marcha local

1. Copiar los env de ejemplo:

   ```bash
   cp laboratorio/backend/.env.example laboratorio/backend/.env
   ```

2. En `laboratorio/backend/.env`, completar:

   - `JWT_SECRET_KEY`: **tiene que ser exactamente el mismo valor** que
     `JWT_SECRET_KEY` en `tambo/backend/.env` — es lo que hace que un token
     de una app sirva en la otra.
   - `CLOUDINARY_CLOUD_NAME` / `CLOUDINARY_API_KEY` / `CLOUDINARY_API_SECRET`:
     podés reusar la misma cuenta que ya usa `task-verifier` (las fotos se
     suben con el prefijo `laboratorio/...`, no pisan nada de esa app) o
     crear una cuenta nueva.
   - `ANTHROPIC_API_KEY`: podés reusar la misma key que `task-verifier` o
     usar una separada. Sin esto, el login y el CRUD de tipos de análisis
     funcionan igual — solo falla (con 502, no con un resultado inventado)
     el paso de "evaluar la muestra con IA".

3. Desde la raíz del repo:

   ```bash
   docker compose up -d --build laboratorio-backend laboratorio-frontend
   ```

   (o `docker compose up -d --build` para levantar las tres apps juntas).

4. Entrar a `http://localhost:5175` con un usuario `admin` o `laboratorio`
   ya existente en tambo (ej. el admin por defecto de tambo,
   `admin` / `admin123` si no lo cambiaste — ver `../tambo/README.md`).

5. Documentación interactiva de la API: `http://localhost:8002/docs`.

## Flujo de uso

1. **Admin o laboratorio** da de alta un tipo de análisis (ej. "Mastitis")
   con sus criterios en texto para la IA, y le carga fotos de referencia
   (aprobado/rechazado) desde `/admin`.
2. **Laboratorio** elige el tipo de análisis, saca/sube la foto del cultivo
   desde `/muestra/:tipoId` (pantalla mobile-friendly, abre la cámara
   trasera en el celular).
3. El backend manda la foto + las referencias activas + los criterios a
   Claude, guarda el resultado como `pendiente`.
4. **Laboratorio** confirma o corrige el veredicto en `/resultados/:id` —
   recién ahí queda `veredicto_final`, con quién y cuándo lo revisó.

## Agregar un tipo de análisis nuevo

Sin deploy: desde `/admin`, cualquier admin o laboratorista carga el
nombre, el slug y los criterios en texto, y le sube al menos una foto
"aprobado" y una "rechazado". No hace falta reentrenar nada — el modelo de
IA no se ajusta por tipo de análisis, se le manda contexto distinto en cada
llamada.

## Tests

```bash
cd laboratorio/backend
pip install -r requirements.txt
pytest -v
```

Usan SQLite en memoria (con `schema_translate_map` para simular los
schemas de Postgres) y mockean Cloudinary/Anthropic — no necesitan
Postgres real ni credenciales para correr. Cubren: login y rechazo por rol,
alta de tipo de análisis, alta de foto de referencia, y el flujo completo
carga de muestra → IA (mockeada) → revisión humana.
