from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import EtiquetaFoto


class FotoReferencia(Base):
    """Foto modelo que define "cómo se ve un cultivo bien / mal" para un
    tipo de análisis. Solo se guarda la URL (Cloudinary) — el binario nunca
    toca la base de datos."""

    __tablename__ = "fotos_referencia"
    __table_args__ = {"schema": "laboratorio"}

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo_analisis_id: Mapped[int] = mapped_column(
        ForeignKey("laboratorio.tipos_analisis.id", ondelete="CASCADE"), nullable=False, index=True
    )
    imagen_url: Mapped[str] = mapped_column(String(500), nullable=False)
    etiqueta: Mapped[EtiquetaFoto] = mapped_column(Enum(EtiquetaFoto, name="etiqueta_foto"), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text(), nullable=True)
    # Referencia lógica a public.users.id (quién la subió) — sin ForeignKey
    # real de Postgres: esa tabla la migra y es dueña tambo, no laboratorio
    # (ver nota en app/models/user.py). El rol de laboratorio solo tiene
    # SELECT sobre users, no REFERENCES, así que una FK real no aplicaría.
    subido_por: Mapped[int] = mapped_column(Integer, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
