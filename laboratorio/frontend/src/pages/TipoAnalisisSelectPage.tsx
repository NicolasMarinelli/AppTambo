import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { apiClient } from "../api/client";
import type { TipoAnalisis } from "../api/types";

export function TipoAnalisisSelectPage() {
  const [tipos, setTipos] = useState<TipoAnalisis[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient
      .get<TipoAnalisis[]>("/tipos-analisis")
      .then((res) => setTipos(res.data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Cargando...</p>;

  return (
    <div>
      <h2>¿Qué análisis vas a hacer?</h2>
      {tipos.length === 0 && (
        <p>
          Todavía no hay tipos de análisis configurados. Un admin o laboratorista puede crear uno desde{" "}
          <Link to="/admin">Tipos de análisis y fotos modelo</Link>.
        </p>
      )}
      <div style={{ display: "grid", gap: "1rem", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))" }}>
        {tipos.map((tipo) => (
          <Link
            key={tipo.id}
            to={`/muestra/${tipo.id}`}
            className="card"
            style={{ textDecoration: "none", color: "inherit" }}
          >
            <h3 style={{ marginBottom: "0.4rem" }}>{tipo.nombre}</h3>
            {tipo.descripcion && (
              <p style={{ color: "var(--color-text-muted)", fontSize: "0.85rem" }}>{tipo.descripcion}</p>
            )}
          </Link>
        ))}
      </div>
    </div>
  );
}
