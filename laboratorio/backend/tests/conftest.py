import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models.enums import UserRole
from app.models.user import User

# SQLite en memoria no entiende schemas de Postgres ("laboratorio",
# "public"): schema_translate_map los "aplana" a la base default para
# poder testear la lógica de negocio sin levantar un Postgres real. Se
# importa User acá a propósito (a diferencia de alembic/env.py) para que
# la tabla exista en la base de test y se pueda loguear.
#
# StaticPool: FastAPI corre los endpoints sync en un threadpool (hilos
# distintos al del test); sin StaticPool, el pool default de SQLite abre
# una conexión nueva (con la base vacía) por cada hilo y las tablas
# "desaparecen" de forma intermitente. StaticPool fuerza una única
# conexión compartida por todo el proceso.
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
connectable = engine.execution_options(schema_translate_map={"laboratorio": None, "public": None})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connectable)


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=connectable)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=connectable)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _make_user(db_session, username: str, role: UserRole) -> User:
    user = User(username=username, password_hash=hash_password("secret123"), role=role, is_active=True)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def admin_user(db_session):
    return _make_user(db_session, "admin_test", UserRole.admin)


@pytest.fixture()
def lab_user(db_session):
    return _make_user(db_session, "lab_test", UserRole.laboratorio)


@pytest.fixture()
def operario_user(db_session):
    return _make_user(db_session, "operario_test", UserRole.operario)


def login_headers(client, username: str, password: str = "secret123") -> dict:
    resp = client.post("/auth/login", json={"username": username, "password": password})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
