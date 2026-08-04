from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.empresa import Empresa, PlanEmpresa
from app.services.empresa_service import (
    get_empresa_or_404, renovar_membresia, cambiar_plan, get_info_empresa
)
from app.config import settings
from pydantic import BaseModel
from datetime import timezone

router = APIRouter()


def verify_admin(x_admin_key: str = Header(...)):
    """Protege todas las rutas de admin con una API key."""
    if x_admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="No autorizado")


class CambiarPlanRequest(BaseModel):
    plan: PlanEmpresa
    ajuste_creditos: int = 0  # créditos extra a sumar/restar manualmente


@router.get("/empresas")
def listar_empresas(
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin),
):
    """Lista todas las empresas con su estado."""
    empresas = db.query(Empresa).order_by(Empresa.creado_en.desc()).all()
    return [
        {
            "id": e.id,
            "nombre": e.nombre,
            "email_contacto": e.email_contacto,
            "plan": e.plan,
            "creditos_disponibles": e.creditos_disponibles,
            "creditos_mensuales": e.creditos_mensuales,
            "membresia_activa": e.membresia_activa,
            "fecha_vencimiento": e.fecha_vencimiento,
            "total_usuarios": len(e.usuarios),
        }
        for e in empresas
    ]


@router.post("/empresas/{empresa_id}/renovar")
def renovar(
    empresa_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin),
):
    """Renueva membresía 30 días y suma créditos mensuales."""
    empresa = renovar_membresia(db, empresa_id)
    return {
        "mensaje": f"Membresía renovada. Créditos disponibles: {empresa.creditos_disponibles}",
        "empresa": get_info_empresa(db, empresa_id),
    }


@router.patch("/empresas/{empresa_id}/plan")
def actualizar_plan(
    empresa_id: int,
    data: CambiarPlanRequest,
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin),
):
    """Cambia el plan y ajusta créditos manualmente si es necesario."""
    empresa = cambiar_plan(db, empresa_id, data.plan)
    if data.ajuste_creditos != 0:
        empresa.creditos_disponibles = max(
            0, empresa.creditos_disponibles + data.ajuste_creditos
        )
        db.commit()
        db.refresh(empresa)
    return get_info_empresa(db, empresa_id)