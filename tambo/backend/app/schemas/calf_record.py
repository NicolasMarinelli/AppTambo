from datetime import date, datetime, time

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.enums import CalostroTipo, TipoCria

PESO_MIN_KG = 15
PESO_MAX_KG = 80
BRIX_MIN = 0
BRIX_MAX = 40


class CalfRecordBase(BaseModel):
    fecha_nacimiento: date = Field(..., description="Fecha de nacimiento del ternero")
    hora_parto: time = Field(..., description="Hora en la que ocurrió el parto")
    madre_caravana: str | None = Field(
        None, description="Caravana de la madre. Se acepta texto libre si no existe en el padrón de animales."
    )
    parto_asistido: bool = Field(False, description="Si el parto requirió asistencia")
    mellizo: bool = Field(False, description="Si nació como mellizo")
    peso_nacimiento_kg: float = Field(..., description=f"Peso al nacer en kg (entre {PESO_MIN_KG} y {PESO_MAX_KG})")
    tipo_cria: TipoCria = Field(..., description="Resultado del parto: macho/hembra vivo/muerto")

    calostro_tipo: CalostroTipo = Field(..., description="Tipo de calostro suministrado")
    calostro_brix: float = Field(..., description=f"Grados Brix medidos (entre {BRIX_MIN} y {BRIX_MAX})")
    calostro_cantidad_litros: float = Field(..., gt=0, description="Cantidad de calostro/leche tomada, en litros")
    calostro_bolsa_numero: str | None = Field(
        None,
        description="Número de bolsa de calostro. Obligatorio si calostro_tipo es natural o mejorado, nulo si es preparado.",
    )

    @field_validator("peso_nacimiento_kg")
    @classmethod
    def validate_peso(cls, value: float) -> float:
        if not (PESO_MIN_KG <= value <= PESO_MAX_KG):
            raise ValueError(f"El peso debe estar entre {PESO_MIN_KG} y {PESO_MAX_KG} kg")
        return value

    @field_validator("calostro_brix")
    @classmethod
    def validate_brix(cls, value: float) -> float:
        if not (BRIX_MIN <= value <= BRIX_MAX):
            raise ValueError(f"Los grados Brix deben estar entre {BRIX_MIN} y {BRIX_MAX}")
        return value

    @model_validator(mode="after")
    def validate_bolsa_numero(self):
        requiere_bolsa = self.calostro_tipo in (CalostroTipo.natural, CalostroTipo.mejorado)
        if requiere_bolsa and not self.calostro_bolsa_numero:
            raise ValueError("El número de bolsa es obligatorio cuando el calostro es natural o mejorado")
        if not requiere_bolsa:
            self.calostro_bolsa_numero = None
        return self


class CalfRecordCreate(CalfRecordBase):
    pass


class CalfRecordUpdate(CalfRecordBase):
    confirm_numbering_change: bool = Field(
        False,
        description=(
            "Debe enviarse en true para confirmar la edición cuando el cambio de tipo_cria "
            "afecta la caravana/SENASA ya asignados. Si no se envía y corresponde advertir, "
            "la API responde 409 con el detalle del cambio."
        ),
    )


class CalfRecordOut(CalfRecordBase):
    id: int
    caravana_asignada: int | None
    numero_senasa: int | None
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NumberingWarning(BaseModel):
    detail: str
    previous_tipo_cria: TipoCria
    new_tipo_cria: TipoCria
    would_lose_caravana: int | None = None
    would_lose_senasa: bool = False
    would_gain_new_numbers: bool = False


class CalfRecordAuditOut(BaseModel):
    id: int
    calf_record_id: int
    previous_state: dict
    edited_by: int
    edited_at: datetime

    model_config = {"from_attributes": True}
