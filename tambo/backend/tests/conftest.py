import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.enums import SequenceName
from app.models.sequence_counter import SequenceCounter

# SQLite in-memory for fast, isolated unit tests of the sequence/business logic.
# The FOR UPDATE lock is a no-op on SQLite but the increment logic itself is
# what's under test here (Postgres row-locking is exercised via manual/integration testing).
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        for name in SequenceName:
            session.add(SequenceCounter(nombre=name, ultimo_valor=0))
        session.commit()
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
