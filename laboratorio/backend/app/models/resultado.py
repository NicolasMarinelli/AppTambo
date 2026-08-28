from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import EstadoResultado, VeredictoIA


class ResultadoLaboratorio(Base):
    """Resultado de un análisis de laboratorio. Pensada para que tambo la
    lea a futuro: vive en la misma base de datos que tambo ("cami"), en el
    schema "laboratorio" — un JOIN directo alcanza, no hace falta ningún
    endpoint intermedio."""

    __tablename__ = "resultados_laboratorio"
    __table_args__ = {"schema": "laboratorio"}

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo_analisis_id: Mapped[int] = mapped_column(
        ForeignKey("laboratorio.tipos_analisis.id"), nullable=False, index=True
    )
    # Referencia lógica a public.users.id — ver nota equivalente en
    # foto_referencia.py (sin FK real, mismo motivo).
    usuario_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    identificacion_muestra: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="Identificación libre de la muestra (caravana, lote, etc.). Sin FK a animals de tambo por ahora.",
    )
    foto_muestra_url: Mapped[str] = mapped_column(String(500), nullable=False)

    ufc: Mapped[str | None] = mapped_column(
        String(50), nullable=True, doc="UFC estimadas. Texto libre para poder representar un rango (ej. '10.000-50.000')."
    )
    veredicto_ia: Mapped[VeredictoIA] = mapped_column(Enum(VeredictoIA, name="veredicto_ia"), nullable=False)
    confianza_ia: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False)
    justificacion_ia: Mapped[str] = mapped_column(Text(), nullable=False)

    # Validación humana (2.3): la IA ayuda, no reemplaza. El resultado
    # queda "pendiente" hasta que un laboratorista confirma o corrige acá.
    veredicto_final: Mapped[VeredictoIA | None] = mapped_column(Enum(VeredictoIA, name="veredicto_ia"), nullable=True)
    revisado_por: Mapped[int | None] = mapped_column(Integer, nullable=True)
    revisado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    estado: Mapped[EstadoResultado] = mapped_column(
        Enum(EstadoResultado, name="estado_resultado"), nullable=False, default=EstadoResultado.pendiente
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
