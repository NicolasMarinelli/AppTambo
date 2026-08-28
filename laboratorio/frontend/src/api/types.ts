export type UserRole = "admin" | "operario" | "laboratorio";

export interface User {
  id: number;
  username: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export type EtiquetaFoto = "aprobado" | "rechazado";
export type VeredictoIA = "aprobado" | "no_aprobado";
export type EstadoResultado = "pendiente" | "aprobado" | "rechazado";

export interface TipoAnalisis {
  id: number;
  nombre: string;
  slug: string;
  descripcion: string | null;
  criterios_ia: string;
  activo: boolean;
  created_at: string;
  updated_at: string;
}

export interface FotoReferencia {
  id: number;
  tipo_analisis_id: number;
  imagen_url: string;
  etiqueta: EtiquetaFoto;
  descripcion: string | null;
  subido_por: number;
  activo: boolean;
  created_at: string;
}

export interface ResultadoLaboratorio {
  id: number;
  tipo_analisis_id: number;
  usuario_id: number;
  identificacion_muestra: string;
  foto_muestra_url: string;
  ufc: string | null;
  veredicto_ia: VeredictoIA;
  confianza_ia: number;
  justificacion_ia: string;
  veredicto_final: VeredictoIA | null;
  revisado_por: number | null;
  revisado_en: string | null;
  estado: EstadoResultado;
  created_at: string;
  updated_at: string;
}

export const VEREDICTO_LABELS: Record<VeredictoIA, string> = {
  aprobado: "Aprobado",
  no_aprobado: "No aprobado",
};
