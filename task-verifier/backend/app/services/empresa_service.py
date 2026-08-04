from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone, timedelta
import secrets
from app.models.empresa import Empresa, CodigoInvitacion, PlanEmpresa
from app.models.user import User
from app.config import settings


CREDITOS_POR_PLAN = {
    PlanEmpresa.basico: settings.CREDITOS_BASICO,
    PlanEmpresa.premium: settings.CREDITOS_PREMIUM,
}


def crear_empresa(
    db: Session,
    nombre: str,
    email_contacto: str,
    plan: PlanEmpresa,
) -> Empresa:
    """Crea una empresa nueva con membresía activa por 30 días."""
    creditos = CREDITOS_POR_PLAN[plan]
    empresa = Empresa(
        nombre=nombre,
        email_contacto=email_contacto,
        plan=plan,
        creditos_disponibles=creditos,
        creditos_mensuales=creditos,
        membresia_activa=True,
        fecha_vencimiento=datetime.now(timezone.utc) + timedelta(days=30),
    )
    db.add(empresa)
    db.commit()
    db.refresh(empresa)
    return empresa


def get_empresa_or_404(db: Session, empresa_id: int) -> Empresa:
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return empresa


def verificar_creditos(db: Session, empresa_id: int) -> None:
    """
    Verifica que la empresa tenga membresía activa y créditos.
    Lanza 402 si no puede proceder.
    """
    empresa = get_empresa_or_404(db, empresa_id)

    # Verificar vencimiento
    ahora = datetime.now(timezone.utc)
    if empresa.fecha_vencimiento.tzinfo is None:
        vencimiento = empresa.fecha_vencimiento.replace(tzinfo=timezone.utc)
    else:
        vencimiento = empresa.fecha_vencimiento

    if ahora > vencimiento:
        empresa.membresia_activa = False
        db.commit()

    if not empresa.membresia_activa:
        raise HTTPException(
            status_code=402,
            detail="Membresía vencida. Contactá al administrador para renovar.",
        )

    if empresa.creditos_disponibles <= 0:
        raise HTTPException(
            status_code=402,
            detail=f"Sin créditos disponibles. Tu plan {empresa.plan} incluye "
                   f"{empresa.creditos_mensuales} créditos mensuales.",
        )


def descontar_credito(db: Session, empresa_id: int) -> None:
    """Descuenta 1 crédito. Llamar DESPUÉS de verificar_creditos."""
    empresa = get_empresa_or_404(db, empresa_id)
    empresa.creditos_disponibles = max(0, empresa.creditos_disponibles - 1)
    db.commit()


def renovar_membresia(db: Session, empresa_id: int) -> Empresa:
    """
    Renueva la membresía por 30 días más y SUMA los créditos del mes.
    Si no renovó el mes anterior, los créditos vencidos NO se acumulan.
    """
    empresa = get_empresa_or_404(db, empresa_id)

    ahora = datetime.now(timezone.utc)
    if empresa.fecha_vencimiento.tzinfo is None:
        base = empresa.fecha_vencimiento.replace(tzinfo=timezone.utc)
    else:
        base = empresa.fecha_vencimiento

    # Si ya venció, la nueva fecha parte desde hoy
    # Si todavía está vigente, extiende desde la fecha actual de vencimiento
    nueva_base = ahora if ahora > base else base
    empresa.fecha_vencimiento = nueva_base + timedelta(days=30)
    empresa.creditos_disponibles += empresa.creditos_mensuales
    empresa.membresia_activa = True

    db.commit()
    db.refresh(empresa)
    return empresa


def cambiar_plan(db: Session, empresa_id: int, nuevo_plan: PlanEmpresa) -> Empresa:
    """Cambia el plan de una empresa. Los créditos mensuales se actualizan."""
    empresa = get_empresa_or_404(db, empresa_id)
    empresa.plan = nuevo_plan
    empresa.creditos_mensuales = CREDITOS_POR_PLAN[nuevo_plan]
    db.commit()
    db.refresh(empresa)
    return empresa


def generar_codigo_invitacion(
    db: Session,
    empresa_id: int,
    rol_destino: str,
) -> CodigoInvitacion:
    """Genera un código de invitación para que un usuario se registre en la empresa."""
    get_empresa_or_404(db, empresa_id)

    codigo = CodigoInvitacion(
        empresa_id=empresa_id,
        codigo=secrets.token_urlsafe(16),
        rol_destino=rol_destino,
        usado=False,
    )
    db.add(codigo)
    db.commit()
    db.refresh(codigo)
    return codigo


def validar_y_usar_codigo(db: Session, codigo_str: str) -> CodigoInvitacion:
    """Valida un código de invitación y lo marca como usado."""
    codigo = db.query(CodigoInvitacion).filter(
        CodigoInvitacion.codigo == codigo_str,
        CodigoInvitacion.usado == False,
    ).first()

    if not codigo:
        raise HTTPException(
            status_code=400,
            detail="Código de invitación inválido o ya utilizado",
        )
    return codigo


def get_info_empresa(db: Session, empresa_id: int) -> dict:
    """Info de créditos y membresía para mostrar al supervisor."""
    empresa = get_empresa_or_404(db, empresa_id)

    ahora = datetime.now(timezone.utc)
    if empresa.fecha_vencimiento.tzinfo is None:
        vencimiento = empresa.fecha_vencimiento.replace(tzinfo=timezone.utc)
    else:
        vencimiento = empresa.fecha_vencimiento

    dias_restantes = max(0, (vencimiento - ahora).days)

    return {
        "nombre": empresa.nombre,
        "plan": empresa.plan,
        "creditos_disponibles": empresa.creditos_disponibles,
        "creditos_mensuales": empresa.creditos_mensuales,
        "membresia_activa": empresa.membresia_activa,
        "fecha_vencimiento": empresa.fecha_vencimiento,
        "dias_restantes": dias_restantes,
    }