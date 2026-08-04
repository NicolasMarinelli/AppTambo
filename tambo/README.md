# Gestión de Nacimientos de Terneros

Sistema para registrar partos de terneros, asignar automáticamente número de
caravana y SENASA, controlar el calostrado, y mantener trazabilidad de
ediciones.

## Stack

- Backend: FastAPI + SQLAlchemy + Alembic + JWT
- Frontend: React + Vite + TypeScript
- Base de datos: PostgreSQL
- Todo orquestado con Docker Compose para desarrollo

## Puesta en marcha local

1. Copiar el archivo de variables de entorno de ejemplo:

   ```bash
   cp .env.example .env
   ```

   Ajustá `JWT_SECRET_KEY` y `DEFAULT_ADMIN_PASSWORD` si vas a usar esto más
   allá de desarrollo local.

2. Levantar todo el entorno:

   ```bash
   docker compose up -d --build
   ```

   Esto levanta:
   - `db`: PostgreSQL en `localhost:5432`
   - `backend`: FastAPI en `http://localhost:8000` (aplica las migraciones de
     Alembic automáticamente al iniciar, incluyendo el seed de usuario admin
     y los contadores de secuencia en 0)
   - `frontend`: Vite dev server en `http://localhost:5173`

3. Ingresar a `http://localhost:5173` con el usuario admin por defecto:

   - Usuario: `admin`
   - Contraseña: `admin123` (definida en `DEFAULT_ADMIN_PASSWORD`)

   **Cambiá esta contraseña en el primer ingreso** desde el panel de usuarios
   (`/admin/usuarios`), o vía `PUT /users/{id}`.

4. La documentación interactiva de la API (Swagger) está en
   `http://localhost:8000/docs`.

## Estructura del repositorio

```
backend/     API FastAPI, modelos SQLAlchemy, migraciones Alembic, tests
frontend/    SPA React + TypeScript
docker-compose.yml
.env.example
```

## Backend en detalle

### Variables de entorno relevantes (ver `.env.example`)

| Variable | Descripción |
|---|---|
| `DATABASE_URL` | Cadena de conexión a Postgres |
| `JWT_SECRET_KEY` | Clave de firma de los JWT — **cambiar en producción** |
| `JWT_EXPIRE_MINUTES` | Minutos de validez del token |
| `DEFAULT_ADMIN_USERNAME` / `DEFAULT_ADMIN_PASSWORD` | Credenciales del usuario admin creado por la migración inicial |
| `CORS_ORIGINS` | Lista JSON de orígenes permitidos para el frontend |

### Migraciones (cómo cambiar el esquema sin perder datos)

La imagen del backend corre `alembic upgrade head` antes de levantar
`uvicorn` (ver `backend/Dockerfile`), y el volumen `db_data` en
`docker-compose.yml` persiste los datos de Postgres entre reinicios. Mientras
no se ejecute `docker volume rm appcami_db_data` ni `docker compose down -v`,
los datos sobreviven a reconstrucciones y reinicios de los contenedores.

Para que un cambio de esquema respete los datos existentes, **no se edita
una migración ya aplicada** (`0001_initial.py` u otra que ya haya corrido
contra la base) — se crea una migración nueva:

1. Editar los modelos en `backend/app/models/...`.
2. Generar la migración comparando contra el estado real de la base:

   ```bash
   docker compose exec backend alembic revision --autogenerate -m "descripcion del cambio"
   ```

3. Revisar el archivo generado en `backend/alembic/versions/`. Autogenerate
   no siempre acierta — en particular, un rename de columna lo detecta como
   "drop + add", lo cual borraría los datos de esa columna. Si es un
   rename, hay que ajustarlo a mano:

   ```python
   op.alter_column("calf_records", "old_name", new_column_name="new_name")
   ```

4. Aplicar la migración reiniciando el backend (el `CMD` del Dockerfile
   corre `alembic upgrade head` en cada arranque):

   ```bash
   docker compose restart backend
   # o, si además cambió código:
   docker compose up -d --build backend
   ```

Reglas prácticas según el tipo de cambio:

| Cambio | Cómo hacerlo sin perder datos |
|---|---|
| Agregar columna o tabla | Aditivo, sin riesgo |
| Renombrar columna | `op.alter_column(..., new_column_name=...)`, nunca drop+create |
| Cambiar tipo de dato | `op.alter_column(..., type_=..., postgresql_using="...")` si Postgres necesita conversión explícita |
| Borrar una columna | Si los datos importan, primero copiarlos a la columna/tabla nueva en la misma migración, recién después borrar la vieja |

Este proyecto llegó a este punto habiendo editado `0001_initial.py`
directamente (renombrar `calostro_cantidad_ml` a `calostro_cantidad_litros`)
porque todavía no había datos reales cargados. De acá en adelante, cualquier
cambio de esquema debe ir en una migración nueva siguiendo lo de arriba.

### Tests

Los tests unitarios cubren la lógica crítica de negocio: asignación atómica
de caravana/SENASA por tipo de cría, y las reglas de validación de
calostro/bolsa (obligatoriedad según tipo, rangos de peso y Brix).

```bash
cd backend
pip install -r requirements.txt
pytest -q
```

Los tests usan SQLite en memoria para velocidad; el `SELECT ... FOR UPDATE`
sobre `sequence_counters` es un no-op en SQLite pero ejercita la misma lógica
de incremento que corre contra Postgres en producción.

### Reglas de negocio implementadas

- **Caravana**: se asigna solo si `tipo_cria` es `macho_vivo` o
  `hembra_viva`, usando el contador correspondiente (`caravana_macho` /
  `caravana_hembra`). Las crías muertas no reciben caravana.
- **SENASA**: se asigna a cualquier cría viva (macho o hembra), usando un
  único contador `senasa` compartido entre ambos sexos.
- **Concurrencia**: la asignación usa `SELECT ... FOR UPDATE` sobre la fila
  del contador dentro de la transacción de la request, evitando que dos
  cargas simultáneas reciban el mismo número.
- **Madre**: el campo `madre_caravana` se ofrece con autocompletado contra
  `animals`, pero acepta texto libre si la caravana no existe en el padrón.
- **Bolsa de calostro**: `calostro_bolsa_numero` es obligatorio solo si
  `calostro_tipo` es `natural` o `mejorado`; se fuerza a `null` si es
  `preparado`. Es un campo de texto simple e indexado, pensado para
  vincularse en el futuro con una tabla de cultivos de calostro por rol
  `laboratorio` (fuera de alcance de esta etapa).
- **Edición con impacto en numeración**: si al editar un registro cambia el
  `tipo_cria` de forma que correspondería asignar o quitar caravana/SENASA
  (ej. se corrigió porque en realidad murió, o al revés), la API responde
  `409` con el detalle del impacto (`NumberingWarning`) a menos que se envíe
  `confirm_numbering_change: true`. Nunca se renumeran otros registros ya
  cargados — solo se ajusta el registro editado.
- **Auditoría**: cada edición de un `calf_record` guarda el estado anterior
  completo en `calf_records_audit`, junto con quién y cuándo editó.

### Roles

- `admin`: acceso total, incluida la gestión de usuarios.
- `operario`: puede cargar y editar terneros, sin gestión de usuarios.
- `laboratorio`: rol reservado para una futura funcionalidad de análisis de
  cultivos de calostro (carga de fotos + clasificación). **No implementada
  en esta etapa** — el rol existe para no tener que migrar permisos después.

## Frontend en detalle

- El JWT se guarda solo en memoria (no en `localStorage`), así que se pierde
  al refrescar la página por diseño — es el costo aceptado por no exponer el
  token a lectura desde el disco/XSS.
- El formulario de carga/edición de terneros muestra la caravana y SENASA
  asignados apenas se guarda el registro, y abre un modal de confirmación si
  el backend responde `409` por impacto en la numeración.
- El listado admite filtros por fecha, tipo de cría y caravana de la madre.

## Fuera de alcance de esta etapa

La funcionalidad de que el rol `laboratorio` suba fotos de cultivos de
calostro y una IA los clasifique automáticamente (vinculando por
`calostro_bolsa_numero`) queda para una etapa futura. El campo
`calostro_bolsa_numero` ya es un string simple e indexado en `calf_records`
para que agregar esa relación después sea directo.

## Asunciones

- Las crías muertas (`macho_muerto` / `hembra_muerta`) no reciben número de
  caravana ni SENASA. Si SENASA exige reportar también las muertas, hay que
  ajustar `TIPO_CRIA_TO_CARAVANA_SEQUENCE` / `LIVE_TIPO_CRIA` en
  `backend/app/models/enums.py`.
- El rol `laboratorio` no tiene funcionalidad real todavía, solo existe como
  rol preparado (sin endpoints ni pantallas propias).
- Login con JWT simple es suficiente (no se implementó SSO ni 2FA).
