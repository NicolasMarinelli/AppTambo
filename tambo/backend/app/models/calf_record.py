from datetime import date, datetime, time

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, Time, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import CalostroTipo, TipoCria


class CalfRecord(Base):
    __tablename__ = "calf_records"

    id: Mapped[int] = mapped_column(primary_key=True)

    fecha_nacimiento: Mapped[date] = mapped_column(Date, nullable=False)
    hora_parto: Mapped[time] = mapped_column(Time, nullable=False)
    madre_caravana: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    parto_asistido: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    mellizo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    peso_nacimiento_kg: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    tipo_cria: Mapped[TipoCria] = mapped_column(Enum(TipoCria, name="tipo_cria"), nullable=False)

    caravana_asignada: Mapped[int | None] = mapped_column(Integer, nullable=True)
    numero_senasa: Mapped[int | None] = mapped_column(Integer, nullable=True)

    calostro_tipo: Mapped[CalostroTipo] = mapped_column(Enum(CalostroTipo, name="calostro_tipo"), nullable=False)
    calostro_brix: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    calostro_cantidad_litros: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    calostro_bolsa_numero: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)

    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
