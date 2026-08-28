import { useState, type ChangeEvent, type FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { apiClient } from "../api/client";
import type { ResultadoLaboratorio } from "../api/types";

// Pantalla pensada para usarse desde el celular en el laboratorio:
// capture="environment" abre directo la cámara trasera en navegadores
// móviles, y el layout es de una sola columna con máximo 480px.
export function UploadSamplePage() {
  const { tipoId } = useParams<{ tipoId: string }>();
  const navigate = useNavigate();
  const [identificacion, setIdentificacion] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    const selected = e.target.files?.[0] ?? null;
    setFile(selected);
    setPreview(selected ? URL.createObjectURL(selected) : null);
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!file || !tipoId) return;

    setSubmitting(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("tipo_analisis_id", tipoId);
      formData.append("identificacion_muestra", identificacion);
      formData.append("file", file);

      const { data } = await apiClient.post<ResultadoLaboratorio>("/resultados", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      navigate(`/resultados/${data.id}`);
    } catch {
      setError("No se pudo evaluar la muestra. Verificá la foto (¿el tipo de análisis tiene fotos modelo cargadas?) e intentá de nuevo.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <h2>Cargar muestra</h2>
      <form
        className="card"
        onSubmit={handleSubmit}
        style={{ display: "flex", flexDirection: "column", gap: "1.1rem", maxWidth: "480px" }}
      >
        <label>
          Identificación de la muestra
          <input
            value={identificacion}
            onChange={(e) => setIdentificacion(e.target.value)}
            placeholder="Ej. Caravana 245, Lote 3..."
            required
          />
        </label>

        <label>
          Foto del cultivo
          <input type="file" accept="image/*" capture="environment" onChange={handleFileChange} required />
        </label>

        {preview && (
          <img
            src={preview}
            alt="Vista previa de la muestra"
            style={{
              width: "100%",
              maxHeight: "320px",
              objectFit: "contain",
              borderRadius: "var(--radius-md)",
              border: "1px solid var(--color-border)",
            }}
          />
        )}

        {error && <p className="form-error">{error}</p>}

        <button type="submit" className="btn-primary" disabled={submitting || !file}>
          {submitting ? "Evaluando con IA..." : "Enviar a evaluar"}
        </button>
      </form>
    </div>
  );
}
