# AppCami

Un único punto de entrada que combina dos microservicios independientes,
cada uno con su propio backend, frontend, base de datos lógica y login.

| Servicio | Descripción | Frontend | Backend / API docs |
|---|---|---|---|
| **task-verifier** | Checklists y verificación de tareas: asignaciones a operarios, respuestas, notificaciones para supervisores. | http://localhost:5173 | http://localhost:8000/docs |
| **tambo** | Gestión de nacimientos de terneros: asignación de caravana/SENASA, control de calostrado, trazabilidad de ediciones. | http://localhost:5174 | http://localhost:8001/docs |
| **landing** | Menú estático que enlaza a los dos frontends de arriba. No comparte sesión ni estado con ninguno. | http://localhost:3000 | — |

Cada app vive en su propia carpeta (`task-verifier/`, `tambo/`) con su
propio código, dependencias y `.env` — son microservicios de verdad, no
capas de un mismo monolito. Lo único que comparten es la instancia de
Postgres (por infraestructura, no por dominio: ver más abajo) y este
`docker-compose.yml` de nivel raíz que los levanta a todos juntos.

## Arquitectura

```
appCami/
├── docker-compose.yml         # levanta todo: db + 2 backends + 2 frontends + landing
├── .env                        # credenciales del Postgres compartido (gitignored)
├── infra/
│   └── postgres-init/          # script que crea un rol+DB por servicio en el Postgres compartido
├── landing/                    # página estática de menú (nginx)
├── task-verifier/               # microservicio 1 — ver task-verifier/README.md si existiera
│   ├── backend/                 # FastAPI + SQLAlchemy + Postgres
│   ├── frontend/                # React + Vite (JS)
│   └── docker-compose.standalone.yml   # para correr solo este servicio con su propio Postgres
└── tambo/                       # microservicio 2
    ├── backend/                 # FastAPI + SQLAlchemy + Alembic + Postgres
    ├── frontend/                # React + Vite + TypeScript
    └── docker-compose.standalone.yml
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
query se comparte entre servicios.

### Puertos

Como los dos backends y los dos frontends usaban por defecto los mismos
puertos (`8000` y `5173`), tambo se remapeó a `8001`/`5174` en el
`docker-compose.yml` combinado. Esto es solo un mapeo de puerto de host —
dentro de sus contenedores ambos siguen escuchando en `8000`/`5173` como
siempre.

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
   ```

   (Si estás clonando este repo ya configurado, es posible que estos
   `.env` ya existan localmente — no se commitean.)

3. Levantar todo:

   ```bash
   docker compose up -d --build
   ```

4. Abrir http://localhost:3000 (menú), o ir directo a
   http://localhost:5173 (task-verifier) / http://localhost:5174 (tambo).

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

## Estado de la integración

- **Auth**: totalmente separada. task-verifier tiene roles
  supervisor/operario/empresa; tambo tiene admin/operario/laboratorio.
  No hay login único ni usuarios compartidos entre las dos apps — es una
  decisión consciente, no un pendiente.
- **Datos**: bases de datos separadas dentro del mismo Postgres, sin
  relaciones cruzadas.
- **Descubrimiento**: el `landing/` es solo un menú de links; no hace de
  API gateway ni de proxy.
