import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { apiClient } from "../api/client";
import { VEREDICTO_LABELS, type ResultadoLaboratorio, type VeredictoIA } from "../api/types";

export function ResultPage() {
  const { resultadoId } = useParams<{ resultadoId: string }>();
  const [resultado, setResultado] = useState<ResultadoLaboratorio | null>(null);
  const [veredictoElegido, setVeredictoElegido] = useState<VeredictoIA>("aprobado");
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!resultadoId) return;
    apiClient.get<ResultadoLaboratorio>(`/resultados/${resultadoId}`).then((res) => {
      setResultado(res.data);
      setVeredictoElegido(res.data.veredicto_ia);
    });
  }, [resultadoId]);

  async function handleConfirm() {
    if (!resultado) return;
    setConfirming(true);
    setError(null);
    try {
      const { data } = await apiClient.patch<ResultadoLaboratorio>(`/resultados/${resultado.id}/revision`, {
        veredicto_final: veredictoElegido,
      });
      setResultado(data);
    } catch {
      setError("No se pudo guardar la revisión.");
    } finally {
      setConfirming(false);
    }
  }

  if (!resultado) return <p>Cargando...</p>;

  const pendiente = resultado.estado === "pendiente";

  return (
    <div>
      <h2>Resultado del análisis</h2>
      <div className="card" style={{ display: "flex", flexDirection: "column", gap: "1rem", maxWidth: "480px" }}>
        <img
          src={resultado.foto_muestra_url}
          alt="Muestra analizada"
          style={{
            width: "100%",
            maxHeight: "320px",
            objectFit: "contain",
            borderRadius: "var(--radius-md)",
            border: "1px solid var(--color-border)",
          }}
        />

        <div>
          <span
            className="badge"
            style={{ background: resultado.veredicto_ia === "aprobado" ? "var(--color-primary)" : "#b3261e" }}
          >
            IA: {VEREDICTO_LABELS[resultado.veredicto_ia]}
          </span>
        </div>

        {resultado.ufc && (
          <p>
            <strong>UFC estimadas:</strong> {resultado.ufc}
          </p>
        )}
        <p>
          <strong>Confianza de la IA:</strong> {Math.round(resultado.confianza_ia * 100)}%
        </p>
        <p>
          <strong>Justificación:</strong> {resultado.justificacion_ia}
        </p>

        {pendiente ? (
          <>
            <p className="subtitle">
              Este es un resultado orientativo — confirmá o corregí el veredicto antes de guardarlo como definitivo.
            </p>
            <label>
              Veredicto final
              <select value={veredictoElegido} onChange={(e) => setVeredictoElegido(e.target.value as VeredictoIA)}>
                <option value="aprobado">Aprobado</option>
                <option value="no_aprobado">No aprobado</option>
              </select>
            </label>
            {error && <p className="form-error">{error}</p>}
            <button className="btn-primary" onClick={handleConfirm} disabled={confirming}>
              {confirming ? "Guardando..." : "Confirmar veredicto"}
            </button>
          </>
        ) : (
          <p>
            <strong>Veredicto final:</strong>{" "}
            {resultado.veredicto_final ? VEREDICTO_LABELS[resultado.veredicto_final] : "-"} (revisado el{" "}
            {resultado.revisado_en ? new Date(resultado.revisado_en).toLocaleString() : "-"})
          </p>
        )}
      </div>
    </div>
  );
}
