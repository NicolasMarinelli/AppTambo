import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { operarioAPI } from "../../api/operario";
import { ArrowLeft, Camera, CheckCircle2, Loader2, AlertCircle, XCircle } from "lucide-react";
import { getFotoUrl } from "../../utils/foto";

export default function Checklist() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [checklist, setChecklist] = useState(null);
  const [loading, setLoading] = useState(true);
  // Estado por item: idle | uploading | success | error
  const [estados, setEstados] = useState({});
  const [resultados, setResultados] = useState({});
  const fileRefs = useRef({});

  useEffect(() => {
    operarioAPI.pendientes().then(({ data }) => {
      const found = data.find((c) => c.id === parseInt(id));
      setChecklist(found || null);
      setLoading(false);
    });
  }, [id]);

  const handleFoto = async (item) => {
    const input = fileRefs.current[item.id];
    if (!input) return;
    input.click();
  };

  const handleConvencional = async (itemId, texto) => {
  setEstados((prev) => ({ ...prev, [itemId]: "uploading" }));
  try {
    await operarioAPI.responderConvencional(itemId, texto);
    setEstados((prev) => ({ ...prev, [itemId]: "success" }));
    const { data: pendientes } = await operarioAPI.pendientes();
    const updated = pendientes.find((c) => c.id === parseInt(id));
    setChecklist(updated);
  } catch {
    setEstados((prev) => ({ ...prev, [itemId]: "error" }));
  }
};

  const handleFileChange = async (item, file) => {
    if (!file) return;

    setEstados((prev) => ({ ...prev, [item.id]: "uploading" }));

    try {
      const { data } = await operarioAPI.responder(item.id, file);
      setResultados((prev) => ({ ...prev, [item.id]: data.resultado_ia }));
      setEstados((prev) => ({ ...prev, [item.id]: "success" }));

      // Recargar checklist para actualizar progreso
      const { data: pendientes } = await operarioAPI.pendientes();
      const updated = pendientes.find((c) => c.id === parseInt(id));
      setChecklist(updated);
    } catch (err) {
      setEstados((prev) => ({ ...prev, [item.id]: "error" }));
    }
  };

  if (loading) return <div className="op-loading">Cargando...</div>;
  if (!checklist) return (
    <div className="op-page">
      <div className="op-empty-state">
        <p>Checklist no encontrado.</p>
        <button className="op-btn-back" onClick={() => navigate(-1)}>Volver</button>
      </div>
    </div>
  );

  const progreso = checklist.total_items > 0
    ? Math.round((checklist.items_completados / checklist.total_items) * 100)
    : 0;

  return (
    <div className="op-page">
      <div className="op-detail-header">
        <button className="op-back-btn" onClick={() => navigate(-1)}>
          <ArrowLeft size={18} />
        </button>
        <div className="op-detail-title">
          <h1>{checklist.nombre}</h1>
          <div className="op-detail-meta">
            <span className={`op-freq op-freq-${checklist.frecuencia}`}>
              {checklist.frecuencia}
            </span>
            <span className="op-progress-text">
              {checklist.items_completados}/{checklist.total_items} completados
            </span>
          </div>
        </div>
      </div>

      {/* Barra de progreso general */}
      <div className="op-global-progress">
        <div className="op-global-bar">
          <div className="op-global-fill" style={{ width: `${progreso}%` }} />
        </div>
        <span>{progreso}%</span>
      </div>

      {checklist.completado && (
        <div className="op-completed-banner">
          <CheckCircle2 size={18} />
          ¡Checklist completado para este período!
        </div>
      )}

      <div className="op-items">
        {checklist.items.sort((a, b) => a.orden - b.orden).map((item) => (
          <ItemCard
            key={item.id}
            item={item}
            tipoChecklist={checklist.tipo}    // ← pasar tipo
            estado={estados[item.id] || (item.ya_respondido ? "success" : "idle")}
            resultado={resultados[item.id]}
            onFoto={() => handleFoto(item)}
            onConvencional={handleConvencional}   // ← nuevo
            fileRef={(el) => { fileRefs.current[item.id] = el; }}
            onFileChange={(file) => handleFileChange(item, file)}
          />
        ))}
      </div>
    </div>
  );
}

function ItemCard({ item, tipoChecklist, estado, resultado, onFoto, onConvencional, fileRef, onFileChange }) {
  const [texto, setTexto] = useState("");
  const fotoConvRef = useRef(null);
  
  const estadoConfig = {
    idle:      { border: "#1e2d45",  bg: "#111827" },
    uploading: { border: "#60a5fa",  bg: "rgba(96,165,250,0.05)" },
    success:   { border: "#00d4aa",  bg: "rgba(0,212,170,0.05)" },
    error:     { border: "#ff4d6d",  bg: "rgba(255,77,109,0.05)" },
  };

  const cfg = estadoConfig[estado] || estadoConfig.idle;

   if (tipoChecklist === "convencional") {
    return (
      <div className={`op-item-card ${estado === "success" ? "" : ""}`}
        style={{
          borderColor: estado === "success" ? "#00d4aa" : "#1e2d45",
          background: estado === "success" ? "rgba(0,212,170,0.05)" : "#111827",
        }}
      >
        <input
          type="file"
          accept="image/*"
          ref={fotoConvRef}
          style={{ display: "none" }}
          onChange={(e) => onFileChange && onFileChange(e.target.files[0])}
        />

        <div className="op-item-top">
          <div className="op-item-info">
            <div className="op-item-pregunta">{item.pregunta}</div>
            {item.descripcion && <div className="op-item-desc">{item.descripcion}</div>}
          </div>
          {estado === "success" && <CheckCircle2 size={20} color="#00d4aa" />}
        </div>

        {estado !== "success" && (
          <div className="op-conv-form">
            <textarea
              value={texto}
              onChange={(e) => setTexto(e.target.value)}
              placeholder="Escribí tu observación o confirmación..."
              className="op-conv-textarea"
              rows={2}
            />
            {item.permite_foto && (
              <button
                className="op-foto-btn"
                style={{ marginBottom: "8px" }}
                onClick={() => fotoConvRef.current.click()}
              >
                <Camera size={14} /> Adjuntar foto (opcional)
              </button>
            )}
            <button
              className="op-foto-btn"
              onClick={() => onConvencional(item.id, texto)}
              disabled={!texto.trim() || estado === "uploading"}
            >
              {estado === "uploading"
                ? <><Loader2 size={14} className="spin" /> Guardando...</>
                : <><CheckCircle2 size={14} /> Completar ítem</>
              }
            </button>
          </div>
        )}
      </div>
    );
  }

  return (
    <div
      className="op-item-card"
      style={{ borderColor: cfg.border, background: cfg.bg }}
    >
      {/* Input file oculto */}
      <input
        type="file"
        accept="image/*"
        capture="environment"
        style={{ display: "none" }}
        ref={fileRef}
        onChange={(e) => onFileChange(e.target.files[0])}
      />

      <div className="op-item-top">
        <div className="op-item-info">
          <div className="op-item-pregunta">{item.pregunta}</div>
          {item.descripcion && (
            <div className="op-item-desc">{item.descripcion}</div>
          )}
        </div>

        {item.foto_referencia_url && (
          <div className="op-item-ref">
            <div className="op-ref-label">Referencia</div>
            <img
              src={getFotoUrl(item.foto_referencia_url)}
              alt="referencia"
              className="op-ref-img"
            />
          </div>
        )}
      </div>

      {/* Resultado IA si existe */}
      {resultado && (
        <div className={`op-ia-result ${resultado.aprobado ? "approved" : "rejected"}`}>
          <div className="op-ia-header">
            {resultado.aprobado
              ? <CheckCircle2 size={15} />
              : <XCircle size={15} />}
            <span>{resultado.aprobado ? "Aprobado" : "Rechazado"} por IA</span>
            <span className="op-ia-conf">
              {Math.round(resultado.confianza * 100)}% confianza
            </span>
          </div>
          <p className="op-ia-obs">{resultado.observacion}</p>
        </div>
      )}

      {/* Botón de acción */}
      <div className="op-item-action">
        {estado === "uploading" ? (
          <button className="op-foto-btn loading" disabled>
            <Loader2 size={16} className="spin" />
            Analizando...
          </button>
        ) : estado === "success" ? (
          <button className="op-foto-btn success" onClick={onFoto}>
            <Camera size={16} />
            Tomar otra foto
          </button>
        ) : estado === "error" ? (
          <button className="op-foto-btn error" onClick={onFoto}>
            <AlertCircle size={16} />
            Reintentar
          </button>
        ) : (
          <button className="op-foto-btn" onClick={onFoto}>
            <Camera size={16} />
            Tomar foto
          </button>
        )}
      </div>
    </div>
  );
}