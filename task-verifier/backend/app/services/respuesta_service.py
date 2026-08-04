from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.respuesta import Respuesta
from app.models.notificacion import Notificacion, TipoNotificacion
from app.models.checklist import ChecklistItem, Checklist, ChecklistAsignacion, TipoChecklist, ModoIA
from app.models.user import User as UserModel
from app.services.ia_service import analizar_foto_seguro

def verificar_asignacion(db: Session, checklist_id: int, operario_id: int) -> bool:
    return db.query(ChecklistAsignacion).filter(
        ChecklistAsignacion.checklist_id == checklist_id,
        ChecklistAsignacion.operario_id == operario_id,
    ).first() is not None


def crear_respuesta_ia(
    db: Session,
    item_id: int,
    operario_id: int,
    foto_url: str,
) -> Respuesta:
    """Respuesta para checklist IA — analiza foto con Claude."""
    item = db.query(ChecklistItem).filter(ChecklistItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_id} no encontrado")

    if not verificar_asignacion(db, item.checklist_id, operario_id):
        raise HTTPException(status_code=403, detail="No tenés asignado este checklist")

    # Verificar créditos
    from app.services.empresa_service import verificar_creditos, descontar_credito
    operario = db.query(UserModel).filter(UserModel.id == operario_id).first()
    if operario and operario.empresa_id:
        verificar_creditos(db, operario.empresa_id)

    # Construir prompt según modo_ia del ítem
    foto_ref = None
    prompt_extra = None

    if item.modo_ia in [ModoIA.foto_referencia, ModoIA.ambas]:
        foto_ref = item.foto_referencia_url
    if item.modo_ia in [ModoIA.prompt, ModoIA.ambas]:
        prompt_extra = item.prompt_referencia

    resultado_ia = analizar_foto_seguro(
        pregunta=item.pregunta,
        foto_respuesta_url=foto_url,
        foto_referencia_url=foto_ref,
        prompt_extra=prompt_extra,
    )

    respuesta = Respuesta(
        item_id=item_id,
        operario_id=operario_id,
        foto_url=foto_url,
        resultado_ia=resultado_ia,
        completado=True,
    )
    db.add(respuesta)
    db.flush()

    if operario and operario.empresa_id:
        descontar_credito(db, operario.empresa_id)

    if not resultado_ia["aprobado"]:
        checklist = db.query(Checklist).filter(Checklist.id == item.checklist_id).first()
        notificacion = Notificacion(
            supervisor_id=checklist.creado_por,
            respuesta_id=respuesta.id,
            tipo=TipoNotificacion.tarea_rechazada,
            mensaje=f"La IA rechazó '{item.pregunta}'. Observación: {resultado_ia['observacion']}",
        )
        db.add(notificacion)

    db.commit()
    db.refresh(respuesta)
    return respuesta


def crear_respuesta_convencional(
    db: Session,
    item_id: int,
    operario_id: int,
    texto: str,
    foto_url: Optional[str] = None,
) -> Respuesta:
    """Respuesta para checklist convencional — checkbox + texto."""
    from typing import Optional

    item = db.query(ChecklistItem).filter(ChecklistItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_id} no encontrado")

    if not verificar_asignacion(db, item.checklist_id, operario_id):
        raise HTTPException(status_code=403, detail="No tenés asignado este checklist")

    respuesta = Respuesta(
        item_id=item_id,
        operario_id=operario_id,
        texto_respuesta=texto,
        foto_opcional_url=foto_url,
        completado=True,
    )
    db.add(respuesta)
    db.flush()

    # Verificar si se completó el checklist entero
    _verificar_checklist_completo(db, item.checklist_id, operario_id, respuesta.id)

    db.commit()
    db.refresh(respuesta)
    return respuesta


def _verificar_checklist_completo(
    db: Session,
    checklist_id: int,
    operario_id: int,
    ultima_respuesta_id: int,
) -> None:
    """Si se completaron todos los ítems, notifica al supervisor."""
    from app.services.pendiente_service import get_periodo_actual

    checklist = db.query(Checklist).filter(Checklist.id == checklist_id).first()
    item_ids = [item.id for item in checklist.items]
    if not item_ids:
        return

    inicio, fin = get_periodo_actual(checklist.frecuencia)

    respuestas = db.query(Respuesta).filter(
        Respuesta.operario_id == operario_id,
        Respuesta.item_id.in_(item_ids),
        Respuesta.completado == True,
        Respuesta.fecha >= inicio,
        Respuesta.fecha < fin,
    ).all()

    respondidos = {r.item_id for r in respuestas}

    if set(item_ids) == respondidos:
        operario = db.query(UserModel).filter(UserModel.id == operario_id).first()
        notificacion = Notificacion(
            supervisor_id=checklist.creado_por,
            respuesta_id=ultima_respuesta_id,
            tipo=TipoNotificacion.tarea_rechazada,  # reutilizamos el tipo por ahora
            mensaje=f"El operario {operario.nombre} completó el checklist '{checklist.nombre}'.",
        )
        db.add(notificacion)


def get_respuestas_item(db: Session, item_id: int, operario_id: int) -> list[Respuesta]:
    return (
        db.query(Respuesta)
        .filter(Respuesta.item_id == item_id, Respuesta.operario_id == operario_id)
        .order_by(Respuesta.fecha.desc())
        .all()
    )


def get_todas_respuestas_supervisor(db: Session, supervisor_id: int) -> list[Respuesta]:
    return (
        db.query(Respuesta)
        .join(ChecklistItem, Respuesta.item_id == ChecklistItem.id)
        .join(Checklist, ChecklistItem.checklist_id == Checklist.id)
        .filter(Checklist.creado_por == supervisor_id)
        .order_by(Respuesta.fecha.desc())
        .all()
    )


def get_respuesta_detalle(db: Session, respuesta_id: int, supervisor_id: int) -> dict:
    respuesta = db.query(Respuesta).filter(Respuesta.id == respuesta_id).first()
    if not respuesta:
        raise HTTPException(status_code=404, detail="Respuesta no encontrada")

    item = db.query(ChecklistItem).filter(ChecklistItem.id == respuesta.item_id).first()
    checklist = db.query(Checklist).filter(Checklist.id == item.checklist_id).first()

    if checklist.creado_por != supervisor_id:
        raise HTTPException(status_code=403, detail="No tenés permiso")

    operario = db.query(UserModel).filter(UserModel.id == respuesta.operario_id).first()

    return {
        "id": respuesta.id,
        "item_id": respuesta.item_id,
        "operario_id": respuesta.operario_id,
        "foto_url": respuesta.foto_url,
        "resultado_ia": respuesta.resultado_ia,
        "texto_respuesta": respuesta.texto_respuesta,
        "foto_opcional_url": respuesta.foto_opcional_url,
        "completado": respuesta.completado,
        "aprobado_supervisor": respuesta.aprobado_supervisor,
        "comentario_supervisor": respuesta.comentario_supervisor,
        "fecha": respuesta.fecha,
        "pregunta": item.pregunta,
        "checklist_nombre": checklist.nombre,
        "operario_nombre": operario.nombre if operario else "",
        "foto_referencia_url": item.foto_referencia_url,
        "tipo_checklist": checklist.tipo,
    }


def dar_feedback(db, respuesta_id, supervisor_id, aprobado, comentario):
    respuesta = db.query(Respuesta).filter(Respuesta.id == respuesta_id).first()
    if not respuesta:
        raise HTTPException(status_code=404, detail="Respuesta no encontrada")

    item = db.query(ChecklistItem).filter(ChecklistItem.id == respuesta.item_id).first()
    checklist = db.query(Checklist).filter(Checklist.id == item.checklist_id).first()

    if checklist.creado_por != supervisor_id:
        raise HTTPException(status_code=403, detail="No tenés permiso")

    respuesta.aprobado_supervisor = aprobado
    respuesta.comentario_supervisor = comentario
    db.commit()
    db.refresh(respuesta)
    return respuesta


def get_estadisticas_ia(db, supervisor_id):
    revisadas = (
        db.query(Respuesta)
        .join(ChecklistItem, Respuesta.item_id == ChecklistItem.id)
        .join(Checklist, ChecklistItem.checklist_id == Checklist.id)
        .filter(Checklist.creado_por == supervisor_id, Respuesta.aprobado_supervisor != None)
        .all()
    )
    pendientes = (
        db.query(Respuesta)
        .join(ChecklistItem, Respuesta.item_id == ChecklistItem.id)
        .join(Checklist, ChecklistItem.checklist_id == Checklist.id)
        .filter(Checklist.creado_por == supervisor_id, Respuesta.aprobado_supervisor == None)
        .count()
    )
    total = len(revisadas)
    correctas = sum(
        1 for r in revisadas
        if r.resultado_ia and r.aprobado_supervisor is not None
        and r.resultado_ia.get("aprobado") == r.aprobado_supervisor
    )
    return {
        "total_revisadas": total,
        "ia_correcta": correctas,
        "ia_incorrecta": total - correctas,
        "precision": round(correctas / total, 2) if total > 0 else 0.0,
        "pendientes_revision": pendientes,
    }