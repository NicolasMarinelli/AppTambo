#!/bin/bash
# Runs once, automatically, the first time the shared "db" container starts
# with an empty data volume (standard Postgres image behavior for anything
# dropped in /docker-entrypoint-initdb.d/).
#
# appCami runs a single Postgres instance shared by all microservices, but
# each service keeps its own role + database, exactly as it did when it had
# its own standalone Postgres container. Nothing in either service's
# DATABASE_URL has to change — same user, same password, same db name,
# just a different host process behind the scenes.
#
# laboratorio is the one exception to "each service has its own database":
# by design it has no users of its own — it reuses tambo's `users` table —
# so instead of a 4th database it gets its own Postgres ROLE inside
# tambo's existing database ("cami"), with:
#   - SELECT-only on every table tambo owns in schema "public" (today just
#     `users`; the ALTER DEFAULT PRIVILEGES below also covers tables tambo
#     creates *later*, so this doesn't need to be touched when tambo's
#     schema grows)
#   - full ownership of its own schema "laboratorio" inside that same
#     database, where its own tables live (tipos_analisis,
#     fotos_referencia, resultados_laboratorio — see
#     laboratorio/backend/alembic/versions/0001_initial.py)
# This means laboratorio can read tambo's users for login, and tambo can
# later read resultados_laboratorio with a plain JOIN — no inter-service
# API needed for either.
set -euo pipefail

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER "${TASK_VERIFIER_DB_USER}" WITH PASSWORD '${TASK_VERIFIER_DB_PASSWORD}';
    CREATE DATABASE "${TASK_VERIFIER_DB_NAME}" OWNER "${TASK_VERIFIER_DB_USER}";
    GRANT ALL PRIVILEGES ON DATABASE "${TASK_VERIFIER_DB_NAME}" TO "${TASK_VERIFIER_DB_USER}";

    CREATE USER "${TAMBO_DB_USER}" WITH PASSWORD '${TAMBO_DB_PASSWORD}';
    CREATE DATABASE "${TAMBO_DB_NAME}" OWNER "${TAMBO_DB_USER}";
    GRANT ALL PRIVILEGES ON DATABASE "${TAMBO_DB_NAME}" TO "${TAMBO_DB_USER}";

    CREATE USER "${LABORATORIO_DB_USER}" WITH PASSWORD '${LABORATORIO_DB_PASSWORD}';
    GRANT CONNECT ON DATABASE "${TAMBO_DB_NAME}" TO "${LABORATORIO_DB_USER}";
EOSQL

# Los GRANT/ALTER DEFAULT PRIVILEGES de abajo son a nivel de schema/tabla,
# no de cluster: hay que conectarse a la base de tambo para que apliquen
# ahí (arriba nos conectamos a $POSTGRES_DB, que es la base "postgres" del
# superusuario, no "cami").
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "${TAMBO_DB_NAME}" <<-EOSQL
    GRANT USAGE ON SCHEMA public TO "${LABORATORIO_DB_USER}";
    ALTER DEFAULT PRIVILEGES FOR ROLE "${TAMBO_DB_USER}" IN SCHEMA public
        GRANT SELECT ON TABLES TO "${LABORATORIO_DB_USER}";

    CREATE SCHEMA IF NOT EXISTS laboratorio AUTHORIZATION "${LABORATORIO_DB_USER}";
EOSQL

echo "init-multiple-dbs: created '${TASK_VERIFIER_DB_NAME}' (owner ${TASK_VERIFIER_DB_USER}), '${TAMBO_DB_NAME}' (owner ${TAMBO_DB_USER}), and role '${LABORATORIO_DB_USER}' (SELECT on ${TAMBO_DB_NAME}.public, owner of ${TAMBO_DB_NAME}.laboratorio)"
