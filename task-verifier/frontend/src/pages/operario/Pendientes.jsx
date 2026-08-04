import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { operarioAPI } from "../../api/operario";
import { CheckCircle2, Circle, ChevronRight, ClipboardCheck } from "lucide-react";
import "./Operario.css";

export default function Pendientes() {
  const navigate = useNavigate();
  const [checklists, setChecklists] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    operarioAPI.pendientes()
      .then(({ data }) => setChecklists(data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="op-loading">Cargando tus tareas...</div>;

  const pendientes = checklists.filter((c) => !c.completado);
  const completados = checklists.filter((c) => c.completado);

  return (
    <div className="op-page">
      <div className="op-page-header">
        <h1>Mis tareas</h1>
        <p>
          {pendientes.length === 0
            ? "¡Todo al día! No tenés tareas pendientes."
            : `${pendientes.length} checklist${pendientes.length > 1 ? "s" : ""} pendiente${pendientes.length > 1 ? "s" : ""}`}
        </p>
      </div>

      {checklists.length === 0 && (
        <div className="op-empty-state">
          <ClipboardCheck size={48} strokeWidth={1} />
          <p>No tenés checklists asignados todavía.</p>
        </div>
      )}

      {pendientes.length > 0 && (
        <div className="op-section">
          <h2 className="op-section-title">Pendientes</h2>
          <div className="op-checklist-list">
            {pendientes.map((c) => (
              <ChecklistCard
                key={c.id}
                checklist={c}
                onClick={() => navigate(`/operario/checklist/${c.id}`)}
              />
            ))}
          </div>
        </div>
      )}

      {completados.length > 0 && (
        <div className="op-section">
          <h2 className="op-section-title">Completados hoy</h2>
          <div className="op-checklist-list">
            {completados.map((c) => (
              <ChecklistCard
                key={c.id}
                checklist={c}
                onClick={() => navigate(`/operario/checklist/${c.id}`)}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function ChecklistCard({ checklist, onClick }) {
  const progreso = checklist.total_items > 0
    ? Math.round((checklist.items_completados / checklist.total_items) * 100)
    : 0;

  return (
    <div className={`op-card ${checklist.completado ? "completed" : ""}`} onClick={onClick}>
      <div className="op-card-left">
        <div className="op-card-icon">
          {checklist.completado
            ? <CheckCircle2 size={22} color="#00d4aa" />
            : <Circle size={22} color="#8892a4" />}
        </div>
        <div className="op-card-info">
          <div className="op-card-title">{checklist.nombre}</div>
          {checklist.descripcion && (
            <div className="op-card-desc">{checklist.descripcion}</div>
          )}
          <div className="op-card-meta">
            <span className={`op-freq op-freq-${checklist.frecuencia}`}>
              {checklist.frecuencia}
            </span>
            <span className="op-progress-text">
              {checklist.items_completados}/{checklist.total_items} ítems
            </span>
          </div>
          <div className="op-progress-bar">
            <div className="op-progress-fill" style={{ width: `${progreso}%` }} />
          </div>
        </div>
      </div>
      <ChevronRight size={18} color="#8892a4" />
    </div>
  );
}