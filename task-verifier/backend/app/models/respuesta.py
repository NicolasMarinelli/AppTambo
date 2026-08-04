from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Respuesta(Base):
    __tablename__ = "respuestas"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("checklist_items.id"), nullable=False)
    operario_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Foto subida por el operario
    foto_url = Column(String(500), nullable=True)   

    # Resultado de la IA: { aprobado, confianza, observacion }
    resultado_ia = Column(JSON, nullable=True)

    # Para checklists convencionales
    texto_respuesta = Column(Text, nullable=True)        # ← nuevo
    foto_opcional_url = Column(String(500), nullable=True)  # ← nuevo
    completado = Column(Boolean, default=False, nullable=False)  # ← nuevo

    # Feedback del supervisor: None = sin revisar, True = IA tuvo razón, False = IA se equivocó
    aprobado_supervisor = Column(Boolean, nullable=True)
    comentario_supervisor = Column(Text, nullable=True)

    fecha = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    item = relationship("ChecklistItem", back_populates="respuestas")
    operario = relationship("User", back_populates="respuestas")
    notificacion = relationship("Notificacion", back_populates="respuesta", uselist=False)