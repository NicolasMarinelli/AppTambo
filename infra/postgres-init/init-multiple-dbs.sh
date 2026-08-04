#!/bin/bash
# Runs once, automatically, the first time the shared "db" container starts
# with an empty data volume (standard Postgres image behavior for anything
# dropped in /docker-entrypoint-initdb.d/).
#
# appCami runs a single Postgres instance shared by both microservices, but
# each service keeps its own role + database, exactly as it did when it had
# its own standalone Postgres container. Nothing in either service's
# DATABASE_URL has to change — same user, same password, same db name,
# just a different host process behind the scenes.
set -euo pipefail

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER "${TASK_VERIFIER_DB_USER}" WITH PASSWORD '${TASK_VERIFIER_DB_PASSWORD}';
    CREATE DATABASE "${TASK_VERIFIER_DB_NAME}" OWNER "${TASK_VERIFIER_DB_USER}";
    GRANT ALL PRIVILEGES ON DATABASE "${TASK_VERIFIER_DB_NAME}" TO "${TASK_VERIFIER_DB_USER}";

    CREATE USER "${TAMBO_DB_USER}" WITH PASSWORD '${TAMBO_DB_PASSWORD}';
    CREATE DATABASE "${TAMBO_DB_NAME}" OWNER "${TAMBO_DB_USER}";
    GRANT ALL PRIVILEGES ON DATABASE "${TAMBO_DB_NAME}" TO "${TAMBO_DB_USER}";
EOSQL

echo "init-multiple-dbs: created '${TASK_VERIFIER_DB_NAME}' (owner ${TASK_VERIFIER_DB_USER}) and '${TAMBO_DB_NAME}' (owner ${TAMBO_DB_USER})"
