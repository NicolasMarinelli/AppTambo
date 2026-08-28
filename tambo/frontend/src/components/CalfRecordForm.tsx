import { useEffect, useState, type FormEvent } from "react";
import axios from "axios";

import { apiClient } from "../api/client";
import type {
  CalfRecord,
  CalfRecordInput,
  CalostroTipo,
  NextNumbering,
  NumberingWarning,
  TipoCria,
} from "../api/types";
import { CALOSTRO_TIPO_LABELS, TIPO_CRIA_LABELS } from "../api/types";
import { MadreAutocomplete } from "./MadreAutocomplete";

interface CalfRecordFormProps {
  recordId?: number;
  initial?: CalfRecord;
  onSaved: (record: CalfRecord) => void;
}

const DEFAULT_CALOSTRO_LITROS = 4;

// Caravana y SENASA solo aplican a crías vivas (ver LIVE_TIPO_CRIA en el
// backend) — mismo criterio replicado acá para mostrar/ocultar los campos.
const TIPOS_CON_NUMERACION: TipoCria[] = ["macho_vivo", "hembra_viva"];

// peso_nacimiento_kg, caravana_asignada y numero_senasa arrancan en blanco
// a propósito: no hay un peso por defecto razonable, y la numeración se
// prellena async apenas se conoce el tipo_cria (ver el efecto más abajo).
type FormState = Omit<CalfRecordInput, "peso_nacimiento_kg" | "caravana_asignada" | "numero_senasa"> & {
  peso_nacimiento_kg: number | "";
  caravana_asignada: number | "";
  numero_senasa: number | "";
};

const emptyForm: FormState = {
  fecha_nacimiento: new Date().toISOString().slice(0, 10),
  hora_parto: "",
  madre_caravana: "",
  parto_asistido: false,
  mellizo: false,
  peso_nacimiento_kg: "",
  tipo_cria: "macho_vivo",
  caravana_asignada: "",
  numero_senasa: "",
  calostro_tipo: "natural",
  calostro_brix: 22,
  calostro_cantidad_litros: DEFAULT_CALOSTRO_LITROS,
  calostro_bolsa_numero: "",
};

function toFormState(record?: CalfRecord): FormState {
  if (!record) return emptyForm;
  return {
    fecha_nacimiento: record.fecha_nacimiento,
    hora_parto: record.hora_parto,
    madre_caravana: record.madre_caravana ?? "",
    parto_asistido: record.parto_asistido,
    mellizo: record.mellizo,
    peso_nacimiento_kg: record.peso_nacimiento_kg,
    tipo_cria: record.tipo_cria,
    caravana_asignada: record.caravana_asignada ?? "",
    numero_senasa: record.numero_senasa ?? "",
    calostro_tipo: record.calostro_tipo,
    calostro_brix: record.calostro_brix,
    calostro_cantidad_litros: record.calostro_cantidad_litros,
    calostro_bolsa_numero: record.calostro_bolsa_numero ?? "",
  };
}

export function CalfRecordForm({ recordId, initial, onSaved }: CalfRecordFormProps) {
  const [form, setForm] = useState<FormState>(toFormState(initial));
  const [error, setError] = useState<string | null>(null);
  const [warning, setWarning] = useState<NumberingWarning | null>(null);
  const [saving, setSaving] = useState(false);
  const [savedRecord, setSavedRecord] = useState<CalfRecord | null>(null);

  const requiereBolsa = form.calostro_tipo === "natural" || form.calostro_tipo === "mejorado";
  const requiereNumeracion = TIPOS_CON_NUMERACION.includes(form.tipo_cria);

  function update<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  // Alta: apenas se conoce (o cambia) el tipo de cría, se pide una
  // sugerencia de caravana/SENASA para prellenar el formulario — el
  // usuario puede editarla antes de guardar. No es una reserva: la
  // asignación atómica de verdad sigue pasando en el backend al guardar.
  // Edición: no aplica, el formulario ya arranca con los valores reales
  // del registro (ver toFormState).
  useEffect(() => {
    if (recordId) return;

    if (!requiereNumeracion) {
      setForm((prev) => ({ ...prev, caravana_asignada: "", numero_senasa: "" }));
      return;
    }

    let cancelled = false;
    apiClient
      .get<NextNumbering>("/calf-records/next-numbering", { params: { tipo_cria: form.tipo_cria } })
      .then(({ data }) => {
        if (cancelled) return;
        setForm((prev) => ({
          ...prev,
          caravana_asignada: data.caravana_asignada ?? "",
          numero_senasa: data.numero_senasa ?? "",
        }));
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [form.tipo_cria, recordId, requiereNumeracion]);

  async function submit(confirmNumberingChange: boolean) {
    if (form.peso_nacimiento_kg === "") {
      setError("Ingresá el peso al nacer.");
      return;
    }

    setSaving(true);
    setError(null);
    try {
      const payload: CalfRecordInput = {
        ...form,
        peso_nacimiento_kg: form.peso_nacimiento_kg,
        madre_caravana: form.madre_caravana || null,
        caravana_asignada: requiereNumeracion && form.caravana_asignada !== "" ? form.caravana_asignada : null,
        numero_senasa: requiereNumeracion && form.numero_senasa !== "" ? form.numero_senasa : null,
        calostro_bolsa_numero: requiereBolsa ? form.calostro_bolsa_numero || null : null,
        confirm_numbering_change: confirmNumberingChange,
      };

      const response = recordId
        ? await apiClient.put<CalfRecord>(`/calf-records/${recordId}`, payload)
        : await apiClient.post<CalfRecord>("/calf-records", payload);

      setWarning(null);
      setSavedRecord(response.data);
      onSaved(response.data);
    } catch (err) {
      const detail = axios.isAxiosError(err) && err.response?.status === 409 ? err.response.data?.detail : undefined;
      if (recordId && detail && typeof detail === "object") {
        // Objeto: es el aviso de "cambiar el tipo de cría afecta la numeración" (ver backend).
        setWarning(detail as NumberingWarning);
      } else if (typeof detail === "string") {
        // String: caravana o SENASA ya usados por otro ternero (validación de unicidad).
        setError(detail);
      } else {
        setError("No se pudo guardar el registro. Verificá los datos e intentá de nuevo.");
      }
    } finally {
      setSaving(false);
    }
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    submit(false);
  }

  return (
    <div className="card">
      <form className="form-grid" onSubmit={handleSubmit}>
        <label>
          Fecha de nacimiento
          <input
            type="date"
            value={form.fecha_nacimiento}
            onChange={(e) => update("fecha_nacimiento", e.target.value)}
            required
          />
        </label>
        <label>
          Hora del parto
          <input
            type="time"
            value={form.hora_parto}
            onChange={(e) => update("hora_parto", e.target.value)}
            required
          />
        </label>

        <div className="full-width">
          <MadreAutocomplete
            value={form.madre_caravana ?? ""}
            onChange={(value) => update("madre_caravana", value)}
          />
        </div>

        <label>
          Parto asistido
          <select
            value={form.parto_asistido ? "si" : "no"}
            onChange={(e) => update("parto_asistido", e.target.value === "si")}
          >
            <option value="no">No</option>
            <option value="si">Sí</option>
          </select>
        </label>
        <label>
          Mellizo
          <select value={form.mellizo ? "si" : "no"} onChange={(e) => update("mellizo", e.target.value === "si")}>
            <option value="no">No</option>
            <option value="si">Sí</option>
          </select>
        </label>

        <label>
          Peso al nacer (kg)
          <input
            type="number"
            step="0.1"
            min={15}
            max={80}
            placeholder="Ej: 35"
            value={form.peso_nacimiento_kg}
            onChange={(e) => update("peso_nacimiento_kg", e.target.value === "" ? "" : Number(e.target.value))}
            required
          />
        </label>
        <label>
          Tipo de cría
          <select value={form.tipo_cria} onChange={(e) => update("tipo_cria", e.target.value as TipoCria)}>
            {Object.entries(TIPO_CRIA_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>

        {requiereNumeracion && (
          <>
            <label>
              Caravana asignada
              <input
                type="number"
                min={1}
                step={1}
                value={form.caravana_asignada}
                onChange={(e) => update("caravana_asignada", e.target.value === "" ? "" : Number(e.target.value))}
                required
              />
            </label>
            <label>
              Número SENASA
              <input
                type="number"
                min={1}
                step={1}
                value={form.numero_senasa}
                onChange={(e) => update("numero_senasa", e.target.value === "" ? "" : Number(e.target.value))}
                required
              />
            </label>
          </>
        )}

        <fieldset className="full-width">
          <legend>Calostrado</legend>
          <div className="form-grid">
            <label>
              Tipo de calostro
              <select
                value={form.calostro_tipo}
                onChange={(e) => update("calostro_tipo", e.target.value as CalostroTipo)}
              >
                {Object.entries(CALOSTRO_TIPO_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Grados Brix
              <input
                type="number"
                step="0.1"
                min={0}
                max={40}
                value={form.calostro_brix}
                onChange={(e) => update("calostro_brix", Number(e.target.value))}
                required
              />
            </label>
            <label>
              Cantidad tomada (litros)
              <input
                type="number"
                step="0.1"
                min={0}
                value={form.calostro_cantidad_litros}
                onChange={(e) => update("calostro_cantidad_litros", Number(e.target.value))}
                required
              />
            </label>
            {requiereBolsa && (
              <label>
                Número de bolsa
                <input
                  value={form.calostro_bolsa_numero ?? ""}
                  onChange={(e) => update("calostro_bolsa_numero", e.target.value)}
                  required
                />
              </label>
            )}
          </div>
        </fieldset>

        {error && <p className="form-error full-width">{error}</p>}

        <div className="full-width">
          <button type="submit" className="btn-primary" disabled={saving}>
            {saving ? "Guardando..." : recordId ? "Guardar cambios" : "Registrar ternero"}
          </button>
        </div>
      </form>

      {savedRecord && (
        <div className="assigned-numbers">
          <strong>Registro guardado.</strong>
          <div>
            Caravana asignada:{" "}
            <span className="badge">{savedRecord.caravana_asignada ?? "sin asignar"}</span>
          </div>
          <div>
            Número SENASA: <span className="badge">{savedRecord.numero_senasa ?? "sin asignar"}</span>
          </div>
        </div>
      )}

      {warning && (
        <div className="modal-backdrop">
          <div className="modal">
            <h3>Atención: esto afecta la numeración</h3>
            <p>{warning.detail}</p>
            {warning.would_lose_caravana !== null && (
              <p>Se perdería la caravana ya asignada: #{warning.would_lose_caravana}.</p>
            )}
            {warning.would_lose_senasa && <p>Se quitará el número SENASA ya asignado.</p>}
            {warning.would_gain_new_numbers && <p>Se asignará una nueva caravana y/o número SENASA.</p>}
            <p>No se renumeran otros registros ya cargados.</p>
            <div className="modal-actions">
              <button onClick={() => setWarning(null)}>Cancelar</button>
              <button className="btn-primary" onClick={() => submit(true)} disabled={saving}>
                Confirmar cambio
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
