from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class RolUsuario(str, enum.Enum):
    supervisor = "supervisor"
    operario = "operario"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol = Column(Enum(RolUsuario), nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True)
    es_principal = Column(Boolean, default=False, nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    

    # Relaciones
    empresa = relationship("Empresa", back_populates="usuarios")
    checklists_creados = relationship("Checklist", back_populates="creador")
    asignaciones = relationship("ChecklistAsignacion", back_populates="operario")
    respuestas = relationship("Respuesta", back_populates="operario")
    notificaciones = relationship("Notificacion", back_populates="supervisor")