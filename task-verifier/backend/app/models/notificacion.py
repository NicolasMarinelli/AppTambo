from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class TipoNotificacion(str, enum.Enum):
    tarea_rechazada = "tarea_rechazada"
    tarea_no_completada = "tarea_no_completada"


class Notificacion(Base):
    __tablename__ = "notificaciones"

    id = Column(Integer, primary_key=True, index=True)
    supervisor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    respuesta_id = Column(Integer, ForeignKey("respuestas.id"), nullable=True)
    tipo = Column(Enum(TipoNotificacion), nullable=False)
    mensaje = Column(String(500), nullable=False)
    leida = Column(Boolean, default=False)
    fecha = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    supervisor = relationship("User", back_populates="notificaciones")
    respuesta = relationship("Respuesta", back_populates="notificacion")