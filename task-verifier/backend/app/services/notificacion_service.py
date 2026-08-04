from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from app.models.notificacion import Notificacion, TipoNotificacion
from app.models.checklist import Checklist, ChecklistItem, ChecklistAsignacion
from app.models.respuesta import Respuesta
from app.models.user import User
from app.services.pendiente_service import get_periodo_actual


def get_notificaciones(
    db: Session,
    supervisor_id: int,
    solo_no_leidas: bool = False,
) -> list[Notificacion]:
    """Lista notificaciones del supervisor, las más recientes primero."""
    query = db.query(Notificacion).filter(
        Notificacion.supervisor_id == supervisor_id
    )
    if solo_no_leidas:
        query = query.filter(Notificacion.leida == False)

    return query.order_by(Notificacion.fecha.desc()).all()


def marcar_leida(db: Session, notificacion_id: int, supervisor_id: int) -> Notificacion:
    """Marca una notificación como leída."""
    from fastapi import HTTPException, status

    notificacion = db.query(Notificacion).filter(
        Notificacion.id == notificacion_id,
        Notificacion.supervisor_id == supervisor_id,
    ).first()

    if not notificacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada",
        )

    notificacion.leida = True
    db.commit()
    db.refresh(notificacion)
    return notificacion


def marcar_todas_leidas(db: Session, supervisor_id: int) -> int:
    """Marca todas las notificaciones como leídas. Retorna cuántas se marcaron."""
    cantidad = db.query(Notificacion).filter(
        Notificacion.supervisor_id == supervisor_id,
        Notificacion.leida == False,
    ).update({"leida": True})
    db.commit()
    return cantidad


def get_detalle_notificacion(
    db: Session,
    notificacion_id: int,
    supervisor_id: int,
) -> dict:
    """Retorna la notificación con toda la info de la respuesta asociada."""
    from fastapi import HTTPException, status

    notificacion = db.query(Notificacion).filter(
        Notificacion.id == notificacion_id,
        Notificacion.supervisor_id == supervisor_id,
    ).first()

    if not notificacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada",
        )

    resultado = {
        "id": notificacion.id,
        "supervisor_id": notificacion.supervisor_id,
        "respuesta_id": notificacion.respuesta_id,
        "tipo": notificacion.tipo,
        "mensaje": notificacion.mensaje,
        "leida": notificacion.leida,
        "fecha": notificacion.fecha,
        "foto_url": None,
        "resultado_ia": None,
        "operario_nombre": None,
        "pregunta": None,
    }

    # Enriquecer con datos de la respuesta si existe
    if notificacion.respuesta_id:
        respuesta = db.query(Respuesta).filter(
            Respuesta.id == notificacion.respuesta_id
        ).first()

        if respuesta:
            resultado["foto_url"] = respuesta.foto_url
            resultado["resultado_ia"] = respuesta.resultado_ia

            operario = db.query(User).filter(User.id == respuesta.operario_id).first()
            if operario:
                resultado["operario_nombre"] = operario.nombre

            item = db.query(ChecklistItem).filter(
                ChecklistItem.id == respuesta.item_id
            ).first()
            if item:
                resultado["pregunta"] = item.pregunta

    return resultado


def verificar_tareas_vencidas(db: Session) -> int:
    """
    Revisa todos los checklists asignados y crea notificaciones
    para los que no fueron completados en el período actual.
    Retorna la cantidad de notificaciones creadas.
    """
    creadas = 0
    ahora = datetime.now(timezone.utc)

    asignaciones = db.query(ChecklistAsignacion).all()

    for asignacion in asignaciones:
        checklist = asignacion.checklist
        operario_id = asignacion.operario_id
        inicio_periodo, fin_periodo = get_periodo_actual(checklist.frecuencia)

        # Verificar si ya mandamos esta notificación hoy para esta asignación
        notif_existente = db.query(Notificacion).filter(
            Notificacion.supervisor_id == checklist.creado_por,
            Notificacion.tipo == TipoNotificacion.tarea_no_completada,
            Notificacion.fecha >= inicio_periodo,
            Notificacion.mensaje.contains(f"operario_id:{operario_id}"),
            Notificacion.mensaje.contains(f"checklist_id:{checklist.id}"),
        ).first()

        if notif_existente:
            continue

        # Ver si el operario completó todos los items en este período
        item_ids = [item.id for item in checklist.items]
        if not item_ids:
            continue

        respuestas = db.query(Respuesta).filter(
            Respuesta.operario_id == operario_id,
            Respuesta.item_id.in_(item_ids),
            Respuesta.fecha >= inicio_periodo,
            Respuesta.fecha < fin_periodo,
        ).all()

        items_respondidos = {r.item_id for r in respuestas}
        items_faltantes = set(item_ids) - items_respondidos

        if items_faltantes:
            operario = db.query(User).filter(User.id == operario_id).first()
            operario_nombre = operario.nombre if operario else f"ID {operario_id}"

            notificacion = Notificacion(
                supervisor_id=checklist.creado_por,
                respuesta_id=None,
                tipo=TipoNotificacion.tarea_no_completada,
                mensaje=(
                    f"El operario {operario_nombre} no completó "
                    f"'{checklist.nombre}' en el período actual. "
                    f"Items faltantes: {len(items_faltantes)}. "
                    f"[operario_id:{operario_id}|checklist_id:{checklist.id}]"
                ),
            )
            db.add(notificacion)
            creadas += 1

    db.commit()
    return creadas