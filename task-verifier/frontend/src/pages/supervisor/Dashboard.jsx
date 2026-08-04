import { useState, useEffect } from "react";
import { checklistsAPI } from "../../api/checklists";
import { notificacionesAPI } from "../../api/notificaciones";
import { ClipboardList, Bell, CheckCircle, Brain } from "lucide-react";
import Badge from "../../components/Badge";
import { getFotoUrl } from "../../utils/foto";

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [respuestas, setRespuestas] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      checklistsAPI.listar(),
      checklistsAPI.estadisticasIA(),
      notificacionesAPI.count(),
      checklistsAPI.todasRespuestas(),
    ]).then(([checklists, ia, notifs, resp]) => {
      setStats({
        checklists: checklists.data.length,
        precision: Math.round((ia.data.precision || 0) * 100),
        noLeidas: notifs.data.no_leidas,
        pendientesRevision: ia.data.pendientes_revision,
      });
      setRespuestas(resp.data.slice(0, 5));
    }).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="sup-loading">Cargando...</div>;

  const cards = [
    { label: "Checklists activos", value: stats?.checklists, icon: <ClipboardList size={22} />, color: "#00d4aa" },
    { label: "Notificaciones sin leer", value: stats?.noLeidas, icon: <Bell size={22} />, color: "#ff4d6d" },
    { label: "Pendientes de revisión", value: stats?.pendientesRevision, icon: <CheckCircle size={22} />, color: "#ffb400" },
    { label: "Precisión de la IA", value: `${stats?.precision}%`, icon: <Brain size={22} />, color: "#60a5fa" },
  ];

  return (
    <div className="sup-page">
      <div className="sup-page-header">
        <h1>Dashboard</h1>
        <p>Resumen general del sistema</p>
      </div>

      <div className="stat-grid">
        {cards.map((card) => (
          <div key={card.label} className="stat-card">
            <div className="stat-icon" style={{ color: card.color, background: `${card.color}18` }}>
              {card.icon}
            </div>
            <div className="stat-info">
              <div className="stat-value">{card.value}</div>
              <div className="stat-label">{card.label}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="sup-section">
        <h2>Últimas respuestas</h2>
        {respuestas.length === 0 ? (
          <div className="sup-empty">Todavía no hay respuestas de operarios.</div>
        ) : (
          <div className="resp-list">
            {respuestas.map((r) => (
              <div key={r.id} className="resp-item">
                <div className="resp-foto">
                  <img src={getFotoUrl(r.foto_url)} alt="respuesta" />
                </div>
                <div className="resp-info">
                  <div className="resp-meta">Item #{r.item_id}</div>
                  <div className="resp-fecha">
                    {new Date(r.fecha).toLocaleString("es-AR")}
                  </div>
                </div>
                <div className="resp-estado">
                  {r.resultado_ia?.aprobado
                    ? <Badge variant="success">Aprobado</Badge>
                    : <Badge variant="danger">Rechazado</Badge>
                  }
                  {r.aprobado_supervisor === null && (
                    <Badge variant="warning">Sin revisar</Badge>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}