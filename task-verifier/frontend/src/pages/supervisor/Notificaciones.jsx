import { useState, useEffect } from "react";
import { notificacionesAPI } from "../../api/notificaciones";
import { checklistsAPI } from "../../api/checklists";
import { Bell, CheckCheck, ThumbsUp, ThumbsDown } from "lucide-react";
import Badge from "../../components/Badge";
import { getFotoUrl } from "../../utils/foto";

export default function Notificaciones() {
  const [notifs, setNotifs] = useState([]);
  const [seleccionada, setSeleccionada] = useState(null);
  const [detalle, setDetalle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [feedbackComentario, setFeedbackComentario] = useState("");
  const [savingFeedback, setSavingFeedback] = useState(false);

  useEffect(() => { cargar(); }, []);

  const cargar = async () => {
    setLoading(true);
    const { data } = await notificacionesAPI.listar();
    setNotifs(data);
    setLoading(false);
  };

  const handleSeleccionar = async (notif) => {
    setSeleccionada(notif);
    setDetalle(null);
    setFeedbackComentario("");
    await notificacionesAPI.marcarLeida(notif.id);
    if (notif.respuesta_id) {
      const { data } = await checklistsAPI.detalleRespuesta(notif.respuesta_id);
      setDetalle(data);
    }
    cargar();
  };

  const handleFeedback = async (aprobado) => {
    if (!detalle) return;
    setSavingFeedback(true);
    await checklistsAPI.darFeedback(detalle.id, {
      aprobado,
      comentario: feedbackComentario || null,
    });
    const { data } = await checklistsAPI.detalleRespuesta(detalle.id);
    setDetalle(data);
    setSavingFeedback(false);
  };

  const handleMarcarTodas = async () => {
    await notificacionesAPI.marcarTodasLeidas();
    cargar();
  };

  if (loading) return <div className="sup-loading">Cargando...</div>;

  return (
    <div className="sup-page">
      <div className="sup-page-header">
        <div>
          <h1>Notificaciones</h1>
          <p>{notifs.filter((n) => !n.leida).length} sin leer</p>
        </div>
        {notifs.some((n) => !n.leida) && (
          <button className="btn-ghost" onClick={handleMarcarTodas}>
            <CheckCheck size={16} /> Marcar todas como leídas
          </button>
        )}
      </div>

      <div className="notif-layout">
        {/* Lista */}
        <div className="notif-list">
          {notifs.length === 0 && (
            <div className="sup-empty-state">
              <Bell size={40} strokeWidth={1} />
              <p>Sin notificaciones por ahora.</p>
            </div>
          )}
          {notifs.map((n) => (
            <div
              key={n.id}
              className={`notif-item ${!n.leida ? "unread" : ""} ${seleccionada?.id === n.id ? "selected" : ""}`}
              onClick={() => handleSeleccionar(n)}
            >
              <div className="notif-dot" style={{ opacity: n.leida ? 0 : 1 }} />
              <div className="notif-content">
                <div className="notif-tipo">
                  <Badge variant={n.tipo === "tarea_rechazada" ? "danger" : "warning"}>
                    {n.tipo === "tarea_rechazada" ? "Rechazada" : "No completada"}
                  </Badge>
                </div>
                <div className="notif-msg">{n.mensaje}</div>
                <div className="notif-fecha">
                  {new Date(n.fecha).toLocaleString("es-AR")}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Detalle */}
        <div className="notif-detalle">
          {!seleccionada && (
            <div className="notif-detalle-empty">
              <Bell size={40} strokeWidth={1} />
              <p>Seleccioná una notificación para ver el detalle</p>
            </div>
          )}

          {seleccionada && detalle && (
            <div className="notif-detalle-content">
              <h3>{detalle.pregunta}</h3>
              <p className="detalle-checklist">{detalle.checklist_nombre}</p>

              <div className="detalle-fotos">
                <div className="foto-block">
                  <div className="foto-label">Foto del operario</div>
                  <img
                    src={getFotoUrl(detalle.foto_url)}
                    alt="respuesta"
                    className="detalle-img"
                  />
                </div>
                {detalle.foto_referencia_url && (
                  <div className="foto-block">
                    <div className="foto-label">Foto de referencia</div>
                    <img
                      src={getFotoUrl(detalle.foto_url)}
                      alt="referencia"
                      className="detalle-img"
                    />
                  </div>
                )}
              </div>

              <div className="ia-resultado">
                <div className="ia-header">
                  <span>Veredicto IA</span>
                  <Badge variant={detalle.resultado_ia?.aprobado ? "success" : "danger"}>
                    {detalle.resultado_ia?.aprobado ? "Aprobado" : "Rechazado"}
                  </Badge>
                  <span className="ia-confianza">
                    {Math.round((detalle.resultado_ia?.confianza || 0) * 100)}% confianza
                  </span>
                </div>
                <p className="ia-observacion">{detalle.resultado_ia?.observacion}</p>
              </div>

              {detalle.aprobado_supervisor === null ? (
                <div className="feedback-section">
                  <div className="feedback-label">¿La IA tuvo razón?</div>
                  <textarea
                    placeholder="Comentario opcional..."
                    value={feedbackComentario}
                    onChange={(e) => setFeedbackComentario(e.target.value)}
                    className="feedback-textarea"
                    rows={2}
                  />
                  <div className="feedback-btns">
                    <button
                      className="btn-feedback approve"
                      onClick={() => handleFeedback(true)}
                      disabled={savingFeedback}
                    >
                      <ThumbsUp size={16} /> Aprobar
                    </button>
                    <button
                      className="btn-feedback reject"
                      onClick={() => handleFeedback(false)}
                      disabled={savingFeedback}
                    >
                      <ThumbsDown size={16} /> Rechazar
                    </button>
                  </div>
                </div>
              ) : (
                <div className="feedback-dado">
                  <Badge variant={detalle.aprobado_supervisor ? "success" : "danger"}>
                    Supervisor: {detalle.aprobado_supervisor ? "Aprobó" : "Rechazó"}
                  </Badge>
                  {detalle.comentario_supervisor && (
                    <p>{detalle.comentario_supervisor}</p>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}