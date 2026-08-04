from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class PlanEmpresa(str, enum.Enum):
    basico = "basico"
    premium = "premium"


class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    email_contacto = Column(String(255), nullable=False)
    plan = Column(Enum(PlanEmpresa), nullable=False, default=PlanEmpresa.basico)
    creditos_disponibles = Column(Integer, default=0, nullable=False)
    creditos_mensuales = Column(Integer, nullable=False)
    membresia_activa = Column(Boolean, default=True, nullable=False)
    fecha_vencimiento = Column(DateTime(timezone=True), nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    usuarios = relationship("User", back_populates="empresa")
    codigos = relationship("CodigoInvitacion", back_populates="empresa", cascade="all, delete-orphan")


class CodigoInvitacion(Base):
    __tablename__ = "codigos_invitacion"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)  # ← ForeignKey agregado
    codigo = Column(String(32), unique=True, nullable=False, index=True)
    rol_destino = Column(String(20), nullable=False)
    usado = Column(Boolean, default=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    empresa = relationship("Empresa", back_populates="codigos")