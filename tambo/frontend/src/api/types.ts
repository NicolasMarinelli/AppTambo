export type UserRole = "admin" | "operario" | "laboratorio";

export interface User {
  id: number;
  username: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export type TipoCria = "macho_vivo" | "macho_muerto" | "hembra_viva" | "hembra_muerta";
export type CalostroTipo = "natural" | "mejorado" | "preparado";

export interface Animal {
  id: number;
  caravana: string;
  sexo: string;
  estado: boolean | null;
  created_at: string;
}

export interface CalfRecord {
  id: number;
  fecha_nacimiento: string;
  hora_parto: string;
  madre_caravana: string | null;
  parto_asistido: boolean;
  mellizo: boolean;
  peso_nacimiento_kg: number;
  tipo_cria: TipoCria;
  caravana_asignada: number | null;
  numero_senasa: number | null;
  calostro_tipo: CalostroTipo;
  calostro_brix: number;
  calostro_cantidad_litros: number;
  calostro_bolsa_numero: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
}

export interface CalfRecordInput {
  fecha_nacimiento: string;
  hora_parto: string;
  madre_caravana: string | null;
  parto_asistido: boolean;
  mellizo: boolean;
  peso_nacimiento_kg: number;
  tipo_cria: TipoCria;
  calostro_tipo: CalostroTipo;
  calostro_brix: number;
  calostro_cantidad_litros: number;
  calostro_bolsa_numero: string | null;
  confirm_numbering_change?: boolean;
}

export interface NumberingWarning {
  detail: string;
  previous_tipo_cria: TipoCria;
  new_tipo_cria: TipoCria;
  would_lose_caravana: number | null;
  would_lose_senasa: boolean;
  would_gain_new_numbers: boolean;
}

export interface CalfRecordAudit {
  id: number;
  calf_record_id: number;
  previous_state: Record<string, unknown>;
  edited_by: number;
  edited_at: string;
}

export const TIPO_CRIA_LABELS: Record<TipoCria, string> = {
  macho_vivo: "Macho vivo",
  macho_muerto: "Macho muerto",
  hembra_viva: "Hembra viva",
  hembra_muerta: "Hembra muerta",
};

export const CALOSTRO_TIPO_LABELS: Record<CalostroTipo, string> = {
  natural: "Natural",
  mejorado: "Mejorado",
  preparado: "Preparado",
};
