from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from app.models.checklist import Checklist, ChecklistItem, ChecklistAsignacion, FrecuenciaChecklist
from app.models.respuesta import Respuesta
from app.schemas.pendiente import ChecklistPendienteResponse, ItemPendienteResponse


def get_periodo_actual(frecuencia: FrecuenciaChecklist) -> tuple[datetime, datetime]:
    """
    Calcula el inicio y fin del período actual según la frecuencia.
    Esto determina si una respuesta "cuenta" para el período vigente.
    """
    ahora = datetime.now(timezone.utc)

    if frecuencia == FrecuenciaChecklist.diaria:
        inicio = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
        fin = inicio + timedelta(days=1)

    elif frecuencia == FrecuenciaChecklist.semanal:
        # Semana empieza el lunes
        dias_desde_lunes = ahora.weekday()
        inicio = (ahora - timedelta(days=dias_desde_lunes)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        fin = inicio + timedelta(weeks=1)

    elif frecuencia == FrecuenciaChecklist.mensual:
        inicio = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # Primer día del mes siguiente
        if ahora.month == 12:
            fin = ahora.replace(year=ahora.year + 1, month=1, day=1,
                                hour=0, minute=0, second=0, microsecond=0)
        else:
            fin = ahora.replace(month=ahora.month + 1, day=1,
                                hour=0, minute=0, second=0, microsecond=0)

    else:  # unica — nunca vence
        inicio = datetime.min.replace(tzinfo=timezone.utc)
        fin = datetime.max.replace(tzinfo=timezone.utc)

    return inicio, fin


def get_pendientes(db: Session, operario_id: int) -> list[ChecklistPendienteResponse]:
    """
    Retorna todos los checklists asignados al operario con el estado
    de cada item en el período actual.
    """
    # Traer todas las asignaciones del operario con sus checklists
    asignaciones = (
        db.query(ChecklistAsignacion)
        .filter(ChecklistAsignacion.operario_id == operario_id)
        .all()
    )

    resultado = []

    for asignacion in asignaciones:
        checklist = asignacion.checklist
        inicio_periodo, fin_periodo = get_periodo_actual(checklist.frecuencia)

        # Traer respuestas del operario en este período para este checklist
        item_ids = [item.id for item in checklist.items]

        respuestas_periodo = (
            db.query(Respuesta)
            .filter(
                Respuesta.operario_id == operario_id,
                Respuesta.item_id.in_(item_ids),
                Respuesta.fecha >= inicio_periodo,
                Respuesta.fecha < fin_periodo,
            )
            .all()
        )

        # Set de item_ids ya respondidos en este período
        items_respondidos = {r.item_id for r in respuestas_periodo}

        # Construir lista de items con estado
        items_con_estado = []
        for item in sorted(checklist.items, key=lambda x: x.orden):
            items_con_estado.append(ItemPendienteResponse(
                id=item.id,
                pregunta=item.pregunta,
                descripcion=item.descripcion,
                foto_referencia_url=item.foto_referencia_url,
                orden=item.orden,
                ya_respondido=item.id in items_respondidos,
                permite_foto=item.permite_foto,
            ))

        items_completados = len(items_respondidos)
        total_items = len(checklist.items)

        resultado.append(ChecklistPendienteResponse(
            id=checklist.id,
            nombre=checklist.nombre,
            descripcion=checklist.descripcion,
            frecuencia=checklist.frecuencia,
            tipo=checklist.tipo,  
            items=items_con_estado,
            total_items=total_items,
            items_completados=items_completados,
            completado=(items_completados == total_items and total_items > 0),
        ))

    # Primero los incompletos, después los completos
    resultado.sort(key=lambda x: x.completado)
    return resultado