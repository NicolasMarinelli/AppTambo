from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_operario_or_admin
from app.core.database import get_db
from app.models.calf_record import CalfRecord
from app.models.calf_record_audit import CalfRecordAudit
from app.models.enums import TipoCria, UserRole
from app.models.user import User
from app.schemas.calf_record import (
    CalfRecordAuditOut,
    CalfRecordCreate,
    CalfRecordOut,
    CalfRecordUpdate,
    NextNumberingOut,
    NumberingWarning,
)
from app.services.sequences import (
    next_sequence_value,
    numbering_impact_of_change,
    peek_sequence_value,
    set_sequence_watermark,
)
from app.models.enums import TIPO_CRIA_TO_CARAVANA_SEQUENCE, LIVE_TIPO_CRIA, SequenceName

router = APIRouter(prefix="/calf-records", tags=["calf-records"])


def _validate_numbering_uniqueness(
    db: Session,
    record_id: int | None,
    caravana_asignada: int | None,
    numero_senasa: int | None,
) -> None:
    """Un usuario puede editar a mano la caravana/SENASA sugeridos — esto
    valida que el valor final no choque con el de otro ternero ya cargado
    (excluyendo el propio registro cuando es una edición)."""
    if caravana_asignada is not None:
        conflict = (
            db.query(CalfRecord)
            .filter(CalfRecord.caravana_asignada == caravana_asignada, CalfRecord.id != (record_id or -1))
            .first()
        )
        if conflict is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"La caravana {caravana_asignada} ya está asignada al ternero #{conflict.id}",
            )

    if numero_senasa is not None:
        conflict = (
            db.query(CalfRecord)
            .filter(CalfRecord.numero_senasa == numero_senasa, CalfRecord.id != (record_id or -1))
            .first()
        )
        if conflict is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El número SENASA {numero_senasa} ya está asignado al ternero #{conflict.id}",
            )


def _record_to_audit_dict(record: CalfRecord) -> dict:
    return {
        "fecha_nacimiento": record.fecha_nacimiento.isoformat(),
        "hora_parto": record.hora_parto.isoformat(),
        "madre_caravana": record.madre_caravana,
        "parto_asistido": record.parto_asistido,
        "mellizo": record.mellizo,
        "peso_nacimiento_kg": float(record.peso_nacimiento_kg),
        "tipo_cria": record.tipo_cria.value,
        "caravana_asignada": record.caravana_asignada,
        "numero_senasa": record.numero_senasa,
        "calostro_tipo": record.calostro_tipo.value,
        "calostro_brix": float(record.calostro_brix),
        "calostro_cantidad_litros": float(record.calostro_cantidad_litros),
        "calostro_bolsa_numero": record.calostro_bolsa_numero,
    }


@router.post(
    "",
    response_model=CalfRecordOut,
    status_code=status.HTTP_201_CREATED,
    description="Registra el nacimiento de un ternero y asigna caravana/SENASA según el tipo de cría",
    dependencies=[Depends(require_operario_or_admin)],
)
def create_calf_record(
    payload: CalfRecordCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    caravana_sequence = TIPO_CRIA_TO_CARAVANA_SEQUENCE.get(payload.tipo_cria)
    needs_senasa = payload.tipo_cria in LIVE_TIPO_CRIA

    # El tipo de cría manda: si no aplica caravana/SENASA para este tipo
    # (ej. una cría muerta), se ignora cualquier valor que haya mandado el
    # formulario para ese campo.
    caravana_asignada = payload.caravana_asignada if caravana_sequence is not None else None
    numero_senasa = payload.numero_senasa if needs_senasa else None

    _validate_numbering_uniqueness(db, None, caravana_asignada, numero_senasa)

    # El formulario prellena estos campos con una sugerencia (ver
    # /next-numbering) que el usuario puede editar. Si la dejó tal cual (o
    # la vació), se autoasigna como antes; si la editó a mano, se respeta
    # ese valor y se sube la marca de agua de la secuencia para que no
    # vuelva a repartirse.
    if caravana_sequence is not None:
        if caravana_asignada is not None:
            set_sequence_watermark(db, caravana_sequence, caravana_asignada)
        else:
            caravana_asignada = next_sequence_value(db, caravana_sequence)
    if needs_senasa and numero_senasa is None:
        numero_senasa = next_sequence_value(db, SequenceName.senasa)
    elif needs_senasa:
        set_sequence_watermark(db, SequenceName.senasa, numero_senasa)

    record = CalfRecord(
        **payload.model_dump(exclude={"caravana_asignada", "numero_senasa"}),
        caravana_asignada=caravana_asignada,
        numero_senasa=numero_senasa,
        created_by=current_user.id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get(
    "",
    response_model=list[CalfRecordOut],
    description="Listado de terneros con filtros por fecha, tipo de cría y madre, y paginación",
    dependencies=[Depends(get_current_user)],
)
def list_calf_records(
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
    tipo_cria: TipoCria | None = None,
    madre_caravana: str | None = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(CalfRecord)

    # Un operario solo ve los terneros que cargó él mismo; admin (y
    # cualquier otro rol que llegue a pegarle a este endpoint) ve todo.
    # Se aplica acá, no solo ocultando el link en el frontend, para que no
    # alcance con pegarle directo a la API para ver registros ajenos.
    if current_user.role == UserRole.operario:
        query = query.filter(CalfRecord.created_by == current_user.id)

    if fecha_desde is not None:
        query = query.filter(CalfRecord.fecha_nacimiento >= fecha_desde)
    if fecha_hasta is not None:
        query = query.filter(CalfRecord.fecha_nacimiento <= fecha_hasta)
    if tipo_cria is not None:
        query = query.filter(CalfRecord.tipo_cria == tipo_cria)
    if madre_caravana:
        query = query.filter(CalfRecord.madre_caravana.ilike(f"%{madre_caravana}%"))

    return (
        query.order_by(CalfRecord.fecha_nacimiento.desc(), CalfRecord.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get(
    "/next-numbering",
    response_model=NextNumberingOut,
    description=(
        "Sugerencia (no reservada) de la próxima caravana/SENASA para un tipo de cría, para "
        "prellenar el formulario de alta. No incrementa ningún contador — la asignación real, "
        "atómica, sigue pasando al guardar."
    ),
    dependencies=[Depends(require_operario_or_admin)],
)
def next_numbering(tipo_cria: TipoCria, db: Session = Depends(get_db)):
    caravana_sequence = TIPO_CRIA_TO_CARAVANA_SEQUENCE.get(tipo_cria)
    return NextNumberingOut(
        caravana_asignada=peek_sequence_value(db, caravana_sequence) if caravana_sequence is not None else None,
        numero_senasa=peek_sequence_value(db, SequenceName.senasa) if tipo_cria in LIVE_TIPO_CRIA else None,
    )


@router.get(
    "/{record_id}",
    response_model=CalfRecordOut,
    description="Detalle de un registro de ternero",
    dependencies=[Depends(get_current_user)],
)
def get_calf_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(CalfRecord).filter(CalfRecord.id == record_id).first()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado")
    return record


@router.put(
    "/{record_id}",
    response_model=CalfRecordOut,
    description=(
        "Edita un registro de ternero. Si el cambio de tipo_cria afecta la caravana/SENASA ya "
        "asignados, responde 409 con el detalle a menos que se envíe confirm_numbering_change=true."
    ),
    dependencies=[Depends(require_operario_or_admin)],
)
def update_calf_record(
    record_id: int,
    payload: CalfRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = db.query(CalfRecord).filter(CalfRecord.id == record_id).first()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado")

    previous_state = _record_to_audit_dict(record)

    caravana_sequence = TIPO_CRIA_TO_CARAVANA_SEQUENCE.get(payload.tipo_cria)
    needs_senasa = payload.tipo_cria in LIVE_TIPO_CRIA

    # Punto de partida: lo que mandó el formulario (el form siempre manda el
    # valor que tiene mostrado, lo haya tocado el usuario o no) — esto es lo
    # que habilita editar caravana/SENASA a mano. Si el tipo de cría no
    # aplica ese campo, se ignora lo que haya venido.
    new_caravana = payload.caravana_asignada if caravana_sequence is not None else None
    new_senasa = payload.numero_senasa if needs_senasa else None

    if payload.tipo_cria != record.tipo_cria:
        caravana_changes, senasa_changes = numbering_impact_of_change(record.tipo_cria, payload.tipo_cria)

        if (caravana_changes or senasa_changes) and not payload.confirm_numbering_change:
            new_caravana_seq = TIPO_CRIA_TO_CARAVANA_SEQUENCE.get(payload.tipo_cria)
            new_needs_senasa = payload.tipo_cria in LIVE_TIPO_CRIA

            warning = NumberingWarning(
                detail=(
                    "Cambiar el tipo de cría de "
                    f"'{record.tipo_cria.value}' a '{payload.tipo_cria.value}' afecta la numeración ya "
                    "asignada. Confirmá el cambio para aplicarlo (no se renumeran otros registros)."
                ),
                previous_tipo_cria=record.tipo_cria,
                new_tipo_cria=payload.tipo_cria,
                would_lose_caravana=record.caravana_asignada if caravana_changes and new_caravana_seq is None else None,
                would_lose_senasa=bool(senasa_changes and not new_needs_senasa and record.numero_senasa is not None),
                would_gain_new_numbers=bool(
                    (caravana_changes and new_caravana_seq is not None)
                    or (senasa_changes and new_needs_senasa)
                ),
            )
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=warning.model_dump())

        if caravana_changes:
            new_caravana_seq = TIPO_CRIA_TO_CARAVANA_SEQUENCE.get(payload.tipo_cria)
            new_caravana = next_sequence_value(db, new_caravana_seq) if new_caravana_seq is not None else None

        if senasa_changes:
            new_needs_senasa = payload.tipo_cria in LIVE_TIPO_CRIA
            new_senasa = next_sequence_value(db, SequenceName.senasa) if new_needs_senasa else None

    _validate_numbering_uniqueness(db, record_id, new_caravana, new_senasa)
    if new_caravana is not None and caravana_sequence is not None:
        set_sequence_watermark(db, caravana_sequence, new_caravana)
    if new_senasa is not None and needs_senasa:
        set_sequence_watermark(db, SequenceName.senasa, new_senasa)

    for field, value in payload.model_dump(
        exclude={"confirm_numbering_change", "caravana_asignada", "numero_senasa"}
    ).items():
        setattr(record, field, value)
    record.caravana_asignada = new_caravana
    record.numero_senasa = new_senasa

    audit = CalfRecordAudit(calf_record_id=record.id, previous_state=previous_state, edited_by=current_user.id)
    db.add(audit)

    db.commit()
    db.refresh(record)
    return record


@router.get(
    "/{record_id}/audit",
    response_model=list[CalfRecordAuditOut],
    description="Histórico de ediciones de un registro de ternero",
    dependencies=[Depends(get_current_user)],
)
def get_calf_record_audit(record_id: int, db: Session = Depends(get_db)):
    record = db.query(CalfRecord).filter(CalfRecord.id == record_id).first()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado")

    return (
        db.query(CalfRecordAudit)
        .filter(CalfRecordAudit.calf_record_id == record_id)
        .order_by(CalfRecordAudit.edited_at.desc())
        .all()
    )
