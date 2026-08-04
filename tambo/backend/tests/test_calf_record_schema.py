import pytest
from pydantic import ValidationError

from app.models.enums import CalostroTipo, TipoCria
from app.schemas.calf_record import CalfRecordCreate

BASE_PAYLOAD = dict(
    fecha_nacimiento="2026-07-01",
    hora_parto="08:30:00",
    madre_caravana="123",
    parto_asistido=False,
    mellizo=False,
    peso_nacimiento_kg=35,
    tipo_cria=TipoCria.macho_vivo,
    calostro_brix=22,
    calostro_cantidad_litros=4,
)


def test_natural_requires_bolsa_numero():
    with pytest.raises(ValidationError):
        CalfRecordCreate(**BASE_PAYLOAD, calostro_tipo=CalostroTipo.natural, calostro_bolsa_numero=None)


def test_mejorado_requires_bolsa_numero():
    with pytest.raises(ValidationError):
        CalfRecordCreate(**BASE_PAYLOAD, calostro_tipo=CalostroTipo.mejorado, calostro_bolsa_numero=None)


def test_natural_with_bolsa_numero_is_valid():
    record = CalfRecordCreate(**BASE_PAYLOAD, calostro_tipo=CalostroTipo.natural, calostro_bolsa_numero="B-001")
    assert record.calostro_bolsa_numero == "B-001"


def test_preparado_forces_bolsa_numero_to_none_even_if_sent():
    record = CalfRecordCreate(**BASE_PAYLOAD, calostro_tipo=CalostroTipo.preparado, calostro_bolsa_numero="B-999")
    assert record.calostro_bolsa_numero is None


def test_preparado_without_bolsa_numero_is_valid():
    record = CalfRecordCreate(**BASE_PAYLOAD, calostro_tipo=CalostroTipo.preparado, calostro_bolsa_numero=None)
    assert record.calostro_bolsa_numero is None


@pytest.mark.parametrize("peso", [10, 90])
def test_peso_out_of_range_rejected(peso):
    payload = {**BASE_PAYLOAD, "peso_nacimiento_kg": peso}
    with pytest.raises(ValidationError):
        CalfRecordCreate(**payload, calostro_tipo=CalostroTipo.preparado, calostro_bolsa_numero=None)


@pytest.mark.parametrize("peso", [15, 35, 80])
def test_peso_in_range_accepted(peso):
    payload = {**BASE_PAYLOAD, "peso_nacimiento_kg": peso}
    record = CalfRecordCreate(**payload, calostro_tipo=CalostroTipo.preparado, calostro_bolsa_numero=None)
    assert record.peso_nacimiento_kg == peso


@pytest.mark.parametrize("brix", [-1, 41])
def test_brix_out_of_range_rejected(brix):
    payload = {**BASE_PAYLOAD, "calostro_brix": brix}
    with pytest.raises(ValidationError):
        CalfRecordCreate(**payload, calostro_tipo=CalostroTipo.preparado, calostro_bolsa_numero=None)


@pytest.mark.parametrize("brix", [0, 20, 40])
def test_brix_in_range_accepted(brix):
    payload = {**BASE_PAYLOAD, "calostro_brix": brix}
    record = CalfRecordCreate(**payload, calostro_tipo=CalostroTipo.preparado, calostro_bolsa_numero=None)
    assert record.calostro_brix == brix
