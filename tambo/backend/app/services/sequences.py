from sqlalchemy.orm import Session

from app.models.enums import (
    TIPO_CRIA_TO_CARAVANA_SEQUENCE,
    LIVE_TIPO_CRIA,
    SequenceName,
    TipoCria,
)
from app.models.sequence_counter import SequenceCounter


def next_sequence_value(db: Session, nombre: SequenceName) -> int:
    """Atomically increment and return the next value for a sequence counter.

    Uses SELECT ... FOR UPDATE to lock the counter row for the duration of the
    caller's transaction, so concurrent requests are serialized and never hand
    out the same number twice.
    """
    counter = (
        db.query(SequenceCounter)
        .filter(SequenceCounter.nombre == nombre)
        .with_for_update()
        .one()
    )
    counter.ultimo_valor += 1
    db.flush()
    return counter.ultimo_valor


def peek_sequence_value(db: Session, nombre: SequenceName) -> int:
    """Read-only preview of the next value a sequence counter would hand out,
    WITHOUT incrementing it (no lock, no side effect). Used to prefill the
    "alta de ternero" form with a suggested caravana/SENASA before the user
    saves anything. It's a suggestion, not a reservation: the real, atomic
    assignment still happens at save time via next_sequence_value (or via
    set_sequence_watermark below, if the user overrides the suggestion) — so
    a stale preview from a race between two concurrent creates can't cause a
    collision, just a possibly-outdated suggestion the user can still edit.
    """
    counter = db.query(SequenceCounter).filter(SequenceCounter.nombre == nombre).one()
    return counter.ultimo_valor + 1


def set_sequence_watermark(db: Session, nombre: SequenceName, value: int) -> None:
    """Ensures a sequence counter never again hands out a value <= `value`.

    Used when a user manually overrides an auto-suggested caravana/SENASA
    with a higher number (e.g. to match a physical tag already in hand) —
    without this, a later auto-assigned number could collide with the one
    just entered by hand.
    """
    counter = (
        db.query(SequenceCounter)
        .filter(SequenceCounter.nombre == nombre)
        .with_for_update()
        .one()
    )
    if value > counter.ultimo_valor:
        counter.ultimo_valor = value
        db.flush()


def numbering_impact_of_change(old_tipo: TipoCria, new_tipo: TipoCria) -> tuple[bool, bool]:
    """Returns (caravana_changes, senasa_changes): whether editing tipo_cria from
    old_tipo to new_tipo requires assigning or clearing caravana/SENASA numbers.
    """
    old_caravana_seq = TIPO_CRIA_TO_CARAVANA_SEQUENCE.get(old_tipo)
    new_caravana_seq = TIPO_CRIA_TO_CARAVANA_SEQUENCE.get(new_tipo)
    old_needs_senasa = old_tipo in LIVE_TIPO_CRIA
    new_needs_senasa = new_tipo in LIVE_TIPO_CRIA

    caravana_changes = old_caravana_seq != new_caravana_seq
    senasa_changes = old_needs_senasa != new_needs_senasa
    return caravana_changes, senasa_changes


def assign_numbering_for_tipo_cria(db: Session, tipo_cria: TipoCria) -> tuple[int | None, int | None]:
    """Returns (caravana_asignada, numero_senasa) for a given tipo_cria.

    Caravana is assigned only for live calves, using the sex-specific counter.
    SENASA number is assigned only for live calves regardless of sex.
    Dead calves (macho_muerto / hembra_muerta) receive neither.
    """
    caravana_asignada: int | None = None
    numero_senasa: int | None = None

    caravana_sequence = TIPO_CRIA_TO_CARAVANA_SEQUENCE.get(tipo_cria)
    if caravana_sequence is not None:
        caravana_asignada = next_sequence_value(db, caravana_sequence)

    if tipo_cria in LIVE_TIPO_CRIA:
        numero_senasa = next_sequence_value(db, SequenceName.senasa)

    return caravana_asignada, numero_senasa
