from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TipoAnalisis(Base):
    """Un tipo de análisis es dato, no código: se da de alta desde la
    pantalla de admin, sin deploy. Agregar un análisis nuevo (ej. "Estado
    de Calostro") es solo crear una fila acá + cargarle fotos de
    referencia (ver FotoReferencia) — no requiere reentrenar ni tocar la
    lógica de IA."""

    __tablename__ = "tipos_analisis"
    __table_args__ = {"schema": "laboratorio"}

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text(), nullable=True)
    criterios_ia: Mapped[str] = mapped_column(
        Text(),
        nullable=False,
        doc="Instrucciones en texto libre que se le mandan a la IA junto con las fotos de referencia.",
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
