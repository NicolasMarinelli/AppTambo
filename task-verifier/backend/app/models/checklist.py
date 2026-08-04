from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class FrecuenciaChecklist(str, enum.Enum):
    diaria = "diaria"
    semanal = "semanal"
    mensual = "mensual"
    unica = "unica"


class TipoChecklist(str, enum.Enum):
    ia = "ia"
    convencional = "convencional"
    
class ModoIA(str, enum.Enum):
    foto_referencia = "foto_referencia"
    prompt = "prompt"
    ambas = "ambas"
    ninguna = "ninguna"



class Checklist(Base):
    __tablename__ = "checklists"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    frecuencia = Column(Enum(FrecuenciaChecklist), nullable=False)
    tipo = Column(String(20), nullable=False, default="ia")  # ← String
    creado_por = Column(Integer, ForeignKey("users.id"), nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())

    creador = relationship("User", back_populates="checklists_creados")
    items = relationship("ChecklistItem", back_populates="checklist", cascade="all, delete-orphan")
    asignaciones = relationship("ChecklistAsignacion", back_populates="checklist", cascade="all, delete-orphan")


class ChecklistItem(Base):
    __tablename__ = "checklist_items"

    id = Column(Integer, primary_key=True, index=True)
    checklist_id = Column(Integer, ForeignKey("checklists.id"), nullable=False)
    pregunta = Column(String(500), nullable=False)
    descripcion = Column(Text, nullable=True)
    orden = Column(Integer, default=0)
    modo_ia = Column(String(20), nullable=False, default="ninguna")  # ← String
    foto_referencia_url = Column(String(500), nullable=True)
    prompt_referencia = Column(Text, nullable=True)
    permite_foto = Column(Boolean, default=False, nullable=False)

    checklist = relationship("Checklist", back_populates="items")
    respuestas = relationship("Respuesta", back_populates="item")


class ChecklistAsignacion(Base):
    __tablename__ = "checklist_asignaciones"

    id = Column(Integer, primary_key=True, index=True)
    checklist_id = Column(Integer, ForeignKey("checklists.id"), nullable=False)
    operario_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    asignado_en = Column(DateTime(timezone=True), server_default=func.now())

    checklist = relationship("Checklist", back_populates="asignaciones")
    operario = relationship("User", back_populates="asignaciones")