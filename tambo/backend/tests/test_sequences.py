from app.models.enums import SequenceName, TipoCria
from app.services.sequences import (
    assign_numbering_for_tipo_cria,
    next_sequence_value,
    numbering_impact_of_change,
)


def test_next_sequence_value_increments(db_session):
    assert next_sequence_value(db_session, SequenceName.caravana_macho) == 1
    assert next_sequence_value(db_session, SequenceName.caravana_macho) == 2
    assert next_sequence_value(db_session, SequenceName.caravana_macho) == 3


def test_sequences_are_independent(db_session):
    assert next_sequence_value(db_session, SequenceName.caravana_macho) == 1
    assert next_sequence_value(db_session, SequenceName.caravana_hembra) == 1
    assert next_sequence_value(db_session, SequenceName.caravana_macho) == 2


def test_macho_vivo_gets_caravana_macho_and_senasa(db_session):
    caravana, senasa = assign_numbering_for_tipo_cria(db_session, TipoCria.macho_vivo)
    assert caravana == 1
    assert senasa == 1


def test_hembra_viva_gets_caravana_hembra_and_senasa(db_session):
    caravana, senasa = assign_numbering_for_tipo_cria(db_session, TipoCria.hembra_viva)
    assert caravana == 1
    assert senasa == 1


def test_macho_muerto_gets_no_numbering(db_session):
    caravana, senasa = assign_numbering_for_tipo_cria(db_session, TipoCria.macho_muerto)
    assert caravana is None
    assert senasa is None


def test_hembra_muerta_gets_no_numbering(db_session):
    caravana, senasa = assign_numbering_for_tipo_cria(db_session, TipoCria.hembra_muerta)
    assert caravana is None
    assert senasa is None


def test_senasa_sequence_shared_across_sexes(db_session):
    _, senasa_1 = assign_numbering_for_tipo_cria(db_session, TipoCria.macho_vivo)
    _, senasa_2 = assign_numbering_for_tipo_cria(db_session, TipoCria.hembra_viva)
    assert senasa_1 == 1
    assert senasa_2 == 2


def test_caravana_sequences_do_not_collide_across_sexes(db_session):
    caravana_macho, _ = assign_numbering_for_tipo_cria(db_session, TipoCria.macho_vivo)
    caravana_hembra, _ = assign_numbering_for_tipo_cria(db_session, TipoCria.hembra_viva)
    caravana_macho_2, _ = assign_numbering_for_tipo_cria(db_session, TipoCria.macho_vivo)
    assert caravana_macho == 1
    assert caravana_hembra == 1
    assert caravana_macho_2 == 2


def test_numbering_impact_no_change_when_tipo_cria_same():
    caravana_changes, senasa_changes = numbering_impact_of_change(TipoCria.macho_vivo, TipoCria.macho_vivo)
    assert not caravana_changes
    assert not senasa_changes


def test_numbering_impact_live_to_dead_loses_both():
    caravana_changes, senasa_changes = numbering_impact_of_change(TipoCria.macho_vivo, TipoCria.macho_muerto)
    assert caravana_changes
    assert senasa_changes


def test_numbering_impact_dead_to_live_gains_both():
    caravana_changes, senasa_changes = numbering_impact_of_change(TipoCria.hembra_muerta, TipoCria.hembra_viva)
    assert caravana_changes
    assert senasa_changes


def test_numbering_impact_sex_change_between_live_changes_caravana_not_senasa():
    caravana_changes, senasa_changes = numbering_impact_of_change(TipoCria.macho_vivo, TipoCria.hembra_viva)
    assert caravana_changes
    assert not senasa_changes


def test_numbering_impact_both_dead_no_change():
    caravana_changes, senasa_changes = numbering_impact_of_change(TipoCria.macho_muerto, TipoCria.hembra_muerta)
    assert not caravana_changes
    assert not senasa_changes
