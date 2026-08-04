import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    operario = "operario"
    laboratorio = "laboratorio"


class TipoCria(str, enum.Enum):
    macho_vivo = "macho_vivo"
    macho_muerto = "macho_muerto"
    hembra_viva = "hembra_viva"
    hembra_muerta = "hembra_muerta"


class CalostroTipo(str, enum.Enum):
    natural = "natural"
    mejorado = "mejorado"
    preparado = "preparado"


class SequenceName(str, enum.Enum):
    caravana_macho = "caravana_macho"
    caravana_hembra = "caravana_hembra"
    senasa = "senasa"


LIVE_TIPO_CRIA = {TipoCria.macho_vivo, TipoCria.hembra_viva}
DEAD_TIPO_CRIA = {TipoCria.macho_muerto, TipoCria.hembra_muerta}

TIPO_CRIA_TO_CARAVANA_SEQUENCE = {
    TipoCria.macho_vivo: SequenceName.caravana_macho,
    TipoCria.hembra_viva: SequenceName.caravana_hembra,
}
