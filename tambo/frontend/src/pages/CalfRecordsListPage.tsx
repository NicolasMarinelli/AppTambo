import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { apiClient } from "../api/client";
import type { CalfRecord, TipoCria } from "../api/types";
import { TIPO_CRIA_LABELS } from "../api/types";
import { useAuth } from "../context/AuthContext";

export function CalfRecordsListPage() {
  const { user } = useAuth();
  const puedeCargar = user?.role === "admin" || user?.role === "operario";
  const [records, setRecords] = useState<CalfRecord[]>([]);
  const [fechaDesde, setFechaDesde] = useState("");
  const [fechaHasta, setFechaHasta] = useState("");
  const [tipoCria, setTipoCria] = useState<TipoCria | "">("");
  const [madre, setMadre] = useState("");
  const [loading, setLoading] = useState(true);

  async function fetchRecords() {
    setLoading(true);
    const { data } = await apiClient.get<CalfRecord[]>("/calf-records", {
      params: {
        fecha_desde: fechaDesde || undefined,
        fecha_hasta: fechaHasta || undefined,
        tipo_cria: tipoCria || undefined,
        madre_caravana: madre || undefined,
      },
    });
    setRecords(data);
    setLoading(false);
  }

  useEffect(() => {
    fetchRecords();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div>
      <h2>Listado de terneros</h2>

      {puedeCargar && (
        <Link to="/nuevo" className="btn-primary btn-cargar-ternero">
          + Cargar ternero
        </Link>
      )}

      {user?.role === "operario" && <p className="list-scope-note">Mostrando solo los terneros que cargaste vos.</p>}

      <form
        className="filters"
        onSubmit={(e) => {
          e.preventDefault();
          fetchRecords();
        }}
      >
        <label>
          Desde
          <input type="date" value={fechaDesde} onChange={(e) => setFechaDesde(e.target.value)} />
        </label>
        <label>
          Hasta
          <input type="date" value={fechaHasta} onChange={(e) => setFechaHasta(e.target.value)} />
        </label>
        <label>
          Tipo de cría
          <select value={tipoCria} onChange={(e) => setTipoCria(e.target.value as TipoCria | "")}>
            <option value="">Todos</option>
            {Object.entries(TIPO_CRIA_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
        <label>
          Madre
          <input value={madre} onChange={(e) => setMadre(e.target.value)} placeholder="Caravana de la madre" />
        </label>
        <button type="submit" className="btn-primary">
          Filtrar
        </button>
      </form>

      {loading ? (
        <p>Cargando...</p>
      ) : (
        <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Madre</th>
              <th>Tipo de cría</th>
              <th>Caravana</th>
              <th>SENASA</th>
              <th>Peso (kg)</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {records.map((record) => (
              <tr key={record.id}>
                <td data-label="Fecha">{record.fecha_nacimiento}</td>
                <td data-label="Madre">{record.madre_caravana ?? "-"}</td>
                <td data-label="Tipo de cría">{TIPO_CRIA_LABELS[record.tipo_cria]}</td>
                <td data-label="Caravana">{record.caravana_asignada ?? "-"}</td>
                <td data-label="SENASA">{record.numero_senasa ?? "-"}</td>
                <td data-label="Peso (kg)">{record.peso_nacimiento_kg}</td>
                <td data-label="">
                  <Link to={`/editar/${record.id}`}>Editar</Link>
                </td>
              </tr>
            ))}
            {records.length === 0 && (
              <tr>
                <td colSpan={7}>No hay registros para los filtros seleccionados.</td>
              </tr>
            )}
          </tbody>
        </table>
        </div>
      )}
    </div>
  );
}
