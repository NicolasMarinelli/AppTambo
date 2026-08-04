from sqlalchemy import Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import SequenceName


class SequenceCounter(Base):
    __tablename__ = "sequence_counters"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[SequenceName] = mapped_column(
        Enum(SequenceName, name="sequence_name"), unique=True, nullable=False
    )
    ultimo_valor: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
