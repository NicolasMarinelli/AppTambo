# AppCami

Un único punto de entrada que combina varios microservicios, cada uno con
su propio backend, frontend y login (con una excepción: ver `laboratorio`
abajo).

| Servicio | Descripción | Frontend | Backend / API docs |
|---|---|---|---|
| **task-verifier** | Checklists y verificación de tareas: asignaciones a operarios, respuestas, notificaciones para supervisores. | http://localhost:5173 | http://localhost:8000/docs |
| **tambo** | Gestión de nacimientos de terneros: asignación de caravana/SENASA, control de calostrado, trazabilidad de ediciones. | http://localhost:5174 | http://localhost:8001/docs |
| **laboratorio** | Evaluación de cultivos (mastitis, calostro, etc.) por IA con visión, con validación humana. Sin usuarios propios: reutiliza el login de tambo. | http://localhost:5175 | http://localhost:8002/docs |
| **landing** | Menú estático que enlaza a los tres frontends de arriba. No comparte sesión ni estado con ninguno — ver nota abajo. | http://localhost:3000 | — |

Cada app vive en su propia carpeta (`task-verifier/`, `tambo/`,
`laboratorio/`) con su propio código, dependencias y `.env` — son
microservicios de verdad, no capas de un mismo monolito. Lo único que
comparten es la instancia de Postgres (por infraestructura, no por
dominio: ver más abajo) y este `docker-compose.yml` de nivel raíz que los
levanta a todos juntos.

## Arquitectura

```
appCami/
├── docker-compose.yml         # levanta todo: db + 3 backends + 3 frontends + landing
├── .env                        # credenciales del Postgres compartido (gitignored)
├── infra/
│   └── postgres-init/          # script que crea un rol+DB por servicio en el Postgres compartido
├── landing/                    # página estática de menú (nginx)
├── task-verifier/               # microservicio 1 — ver task-verifier/README.md si existiera
│   ├── backend/                 # FastAPI + SQLAlchemy + Postgres
│   ├── frontend/                # React + Vite (JS)
│   └── docker-compose.standalone.yml   # para correr solo este servicio con su propio Postgres
├── tambo/                       # microservicio 2
│   ├── backend/                 # FastAPI + SQLAlchemy + Alembic + Postgres
│   ├── frontend/                # React + Vite + TypeScript
│   └── docker-compose.standalone.yml
└── laboratorio/                 # microservicio 3 — ver laboratorio/README.md
    ├── backend/                 # FastAPI + SQLAlchemy + Alembic; SIN base propia, ver abajo
    └── frontend/                 # React + Vite + TypeScript
```

### Por qué una sola instancia de Postgres

Ambas apps traían su propio contenedor de Postgres, ambos escuchando en
`5432` — no pueden convivir tal cual en el mismo host. En vez de correr
dos instancias de Postgres en puertos distintos, la instancia se comparte
y cada servicio mantiene su **propio rol y su propia base de datos**
dentro de ella (creados una sola vez por
`infra/postgres-init/init-multiple-dbs.sh` la primera vez que arranca el
volumen). A nivel aplicación nada cambia: cada `DATABASE_URL` sigue
apuntando al mismo usuario/contraseña/nombre de base que tenía antes,
solo que el proceso de Postgres detrás es compartido. Ninguna tabla ni
query se comparte entre task-verifier y tambo.

**laboratorio es la excepción** a "cada servicio tiene su propia base":
por diseño no tiene usuarios propios (reutiliza `tambo.users` para el
login), así que en vez de una 4ª base de datos separada tiene su propio
**rol** de Postgres dentro de la base de tambo ("cami") — solo lectura
sobre las tablas de tambo, dueño exclusivo de su propio schema
`laboratorio` ahí mismo. Ver `laboratorio/README.md` para el detalle
completo y por qué se eligió esto en vez de una API entre servicios.

### Puertos

Como los backends y frontends usaban por defecto los mismos puertos
(`8000` y `5173`), tambo se remapeó a `8001`/`5174` y laboratorio a
`8002`/`5175` en el `docker-compose.yml` combinado. Esto es solo un mapeo
de puerto de host — dentro de sus contenedores todos siguen escuchando en
`8000`/`5173` como siempre.

## Cómo correr todo junto

1. Copiar el env de nivel raíz (credenciales del Postgres compartido):

   ```bash
   cp .env.example .env
   ```

2. Cada servicio necesita su propio `.env` de backend (y de frontend si
   aplica) — son los que ya traía cada app:

   ```bash
   cp task-verifier/backend/.env.examples task-verifier/backend/.env   # completar SECRET_KEY, ANTHROPIC_API_KEY, etc.
   cp tambo/backend/.env.example tambo/backend/.env                     # completar JWT_SECRET_KEY
   cp laboratorio/backend/.env.example laboratorio/backend/.env         # JWT_SECRET_KEY = el mismo valor que el de tambo
   ```

   (Si estás clonando este repo ya configurado, es posible que estos
   `.env` ya existan localmente — no se commitean.)

3. Levantar todo:

   ```bash
   docker compose up -d --build
   ```

4. Abrir http://localhost:3000 (menú con las tres apps), o ir directo a
   http://localhost:5173 (task-verifier) / http://localhost:5174 (tambo) /
   http://localhost:5175 (laboratorio).

## Cómo correr un solo servicio de forma aislada

Cada app conserva su `docker-compose.standalone.yml` original, con su
propio Postgres en el puerto por defecto (`5432`) y sus puertos
originales (`8000`/`5173`). Útil para desarrollar una sola app sin
levantar la otra:

```bash
cd task-verifier
docker compose -f docker-compose.standalone.yml up -d --build
```

```bash
cd tambo
docker compose -f docker-compose.standalone.yml up -d --build
```

No corras el standalone de una app al mismo tiempo que el
`docker-compose.yml` combinado — competirían por los mismos puertos de
Postgres.

laboratorio no tiene `docker-compose.standalone.yml` propio: por diseño
depende de la base de datos de tambo (ver "Estado de la integración" más
abajo), así que no tiene sentido como servicio aislado — se levanta junto
con tambo desde el `docker-compose.yml` de raíz.

## Estado de la integración

- **Auth**: task-verifier sigue totalmente separada (roles
  supervisor/operario/empresa, sin login ni usuarios compartidos con el
  resto — decisión consciente, no un pendiente). tambo y laboratorio son
  la excepción: comparten login de verdad — mismos usuarios, mismo hash
  de contraseña, mismo secreto de JWT — así que loguearse en cualquiera de
  las dos alcanza para usar la otra (ver `laboratorio/README.md`).
- **Datos**: task-verifier y tambo tienen bases de datos separadas dentro
  del mismo Postgres, sin relaciones cruzadas. laboratorio es la
  excepción: vive en la base de tambo (rol y schema propios, solo lectura
  sobre las tablas de tambo) — ver `laboratorio/README.md`.
- **Descubrimiento**: el `landing/` es solo un menú estático de links a
  las tres apps (task-verifier, tambo, laboratorio); no hace de API
  gateway ni de proxy. Las tres tarjetas son siempre visibles para
  cualquiera que abra `landing` — no hay visibilidad condicional por rol
  ahí (landing no tiene login ni sabe quién está logueado en ninguna de
  las apps; cada una sigue validando rol puertas adentro, del lado del
  backend). Si más adelante se quiere ocultar la tarjeta de laboratorio a
  quien no tenga rol admin/laboratorio, hay que darle a landing alguna
  noción de sesión primero — hoy no la tiene.
