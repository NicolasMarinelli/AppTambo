import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { checklistsAPI } from "../../api/checklists";
import { ArrowLeft, Plus, Trash2, UserPlus, UserMinus, Upload, X, Image } from "lucide-react";
import Badge from "../../components/Badge";
import { getFotoUrl } from "../../utils/foto";

export default function ChecklistDetalle() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [checklist, setChecklist] = useState(null);
  const [asignaciones, setAsignaciones] = useState([]);
  const [operarios, setOperarios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [nuevoItem, setNuevoItem] = useState("");
  const [addingItem, setAddingItem] = useState(false);

  useEffect(() => { cargar(); }, [id]);

  const cargar = async () => {
    setLoading(true);
    const [check, asig, ops] = await Promise.all([
      checklistsAPI.obtener(id),
      checklistsAPI.listarAsignaciones(id),
      checklistsAPI.listarOperarios(),
    ]);
    setChecklist(check.data);
    setAsignaciones(asig.data);
    setOperarios(ops.data);
    setLoading(false);
  };

  const handleAgregarItem = async () => {
    if (!nuevoItem.trim()) return;
    setAddingItem(true);
    await checklistsAPI.agregarItem(id, {
      pregunta: nuevoItem.trim(),
      orden: checklist.items.length,
    });
    setNuevoItem("");
    setAddingItem(false);
    cargar();
  };

  const handleEliminarItem = async (itemId) => {
    if (!confirm("¿Eliminar este ítem?")) return;
    await checklistsAPI.eliminarItem(itemId);
    cargar();
  };

  const handleAsignar = async (operarioId) => {
    await checklistsAPI.asignar(id, operarioId);
    cargar();
  };

  const handleDesasignar = async (operarioId) => {
    await checklistsAPI.desasignar(id, operarioId);
    cargar();
  };

  const asignadosIds = new Set(asignaciones.map((a) => a.operario_id));
  const noAsignados = operarios.filter((o) => !asignadosIds.has(o.id));

  if (loading) return <div className="sup-loading">Cargando...</div>;

  return (
    <div className="sup-page">
      <div className="sup-page-header">
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <button className="btn-ghost icon-only" onClick={() => navigate(-1)}>
            <ArrowLeft size={18} />
          </button>
          <div>
            <h1>{checklist.nombre}</h1>
            <p><Badge variant="info">{checklist.frecuencia}</Badge></p>
          </div>
        </div>
      </div>

      <div className="detalle-grid">
        {/* ── Ítems ── */}
        <div className="detalle-section">
          <h2>Ítems del checklist</h2>
          <div className="items-list">
            {checklist.items.length === 0 && (
              <div className="sup-empty">Sin ítems todavía.</div>
            )}
            {checklist.items
              .sort((a, b) => a.orden - b.orden)
              .map((item, i) => (
                <ItemRow
                  key={item.id}
                  item={item}
                  numero={i + 1}
                  tipoChecklist={checklist.tipo}   // ← pasar tipo
                  onEliminar={() => handleEliminarItem(item.id)}
                  onRefrescar={cargar}
                />
              ))}
          </div>

          <div className="item-input-row" style={{ marginTop: "12px" }}>
            <input
              value={nuevoItem}
              onChange={(e) => setNuevoItem(e.target.value)}
              placeholder="Nueva pregunta..."
              onKeyDown={(e) => e.key === "Enter" && handleAgregarItem()}
            />
            <button
              className="btn-add-item"
              onClick={handleAgregarItem}
              disabled={addingItem}
            >
              <Plus size={16} />
            </button>
          </div>
        </div>

        {/* ── Asignaciones ── */}
        <div className="detalle-section">
          <h2>Operarios asignados</h2>
          {asignaciones.length === 0 ? (
            <div className="sup-empty">Sin operarios asignados.</div>
          ) : (
            <div className="operarios-list">
              {asignaciones.map((a) => (
                <div key={a.id} className="operario-row">
                  <div className="op-avatar">
                    {a.operario.nombre.charAt(0).toUpperCase()}
                  </div>
                  <div className="op-info">
                    <div className="op-name">{a.operario.nombre}</div>
                    <div className="op-email">{a.operario.email}</div>
                  </div>
                  <button
                    className="btn-icon danger"
                    onClick={() => handleDesasignar(a.operario_id)}
                    title="Desasignar"
                  >
                    <UserMinus size={14} />
                  </button>
                </div>
              ))}
            </div>
          )}

          {noAsignados.length > 0 && (
            <>
              <h3 style={{ marginTop: "20px", marginBottom: "10px" }}>
                Agregar operario
              </h3>
              <div className="operarios-list">
                {noAsignados.map((op) => (
                  <div key={op.id} className="operario-row muted">
                    <div className="op-avatar muted">
                      {op.nombre.charAt(0).toUpperCase()}
                    </div>
                    <div className="op-info">
                      <div className="op-name">{op.nombre}</div>
                      <div className="op-email">{op.email}</div>
                    </div>
                    <button
                      className="btn-icon success"
                      onClick={() => handleAsignar(op.id)}
                      title="Asignar"
                    >
                      <UserPlus size={14} />
                    </button>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Componente ItemRow ────────────────────────────────────────────

function ItemRow({ item, numero, tipoChecklist, onEliminar, onRefrescar }) {
  const fileRef = useRef(null);
  const [uploading, setUploading] = useState(false);
  const [preview, setPreview] = useState(
    item.foto_referencia_url
      ? getFotoUrl(item.foto_referencia_url)
      : null
  );
  const [modoIA, setModoIA] = useState(item.modo_ia || "ninguna");
  const [prompt, setPrompt] = useState(item.prompt_referencia || "");
  const [savingConfig, setSavingConfig] = useState(false);

  const handleSaveConfig = async () => {
    setSavingConfig(true);
    try {
      await checklistsAPI.actualizarItem(item.id, {
        modo_ia: modoIA,
        prompt_referencia: prompt || null,
        permite_foto: item.permite_foto,
      });
      onRefrescar();
    } finally {
      setSavingConfig(false);
    }
  };

  const handleEliminarFoto = async () => {
    setUploading(true);
    try {
      await checklistsAPI.eliminarFotoReferencia(item.id);
      setPreview(null);
      onRefrescar();
    } finally {
      setUploading(false);
    }
  };

  const handleFileChange = async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  setPreview(URL.createObjectURL(file));
  setUploading(true);
  try {
    await checklistsAPI.subirFotoReferencia(item.id, file);
    onRefrescar();
  } catch {
    setPreview(
      item.foto_referencia_url
        ? getFotoUrl(item.foto_referencia_url)
        : null
    );
  } finally {
    setUploading(false);
    e.target.value = "";
  }
};


  return (
    <div className="item-row-extended">
      <div className="item-row-top">
        <span className="item-num">{numero}</span>
        <span className="item-text">{item.pregunta}</span>
        <button className="btn-icon danger" onClick={onEliminar}>
          <Trash2 size={13} />
        </button>
      </div>

      {tipoChecklist === "ia" ? (
        // ── Configuración IA ──
        <div className="item-ia-config">
          <div className="field">
            <label>Modo de verificación IA</label>
            <select
              value={modoIA}
              onChange={(e) => setModoIA(e.target.value)}
              className="modo-ia-select"
            >
              <option value="ninguna">Sin referencia — solo contexto del texto</option>
              <option value="foto_referencia">Foto de referencia</option>
              <option value="prompt">Prompt descriptivo</option>
              <option value="ambas">Foto + Prompt</option>
            </select>
          </div>

          {(modoIA === "prompt" || modoIA === "ambas") && (
            <div className="field">
              <label>Prompt de referencia</label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Ej: La máquina debe estar apagada, el área limpia y sin residuos en el piso..."
                className="prompt-textarea"
                rows={3}
              />
            </div>
          )}

          {(modoIA === "foto_referencia" || modoIA === "ambas") && (
            <div className="item-ref-zona">
              <input
                type="file"
                accept="image/*"
                ref={fileRef}
                style={{ display: "none" }}
                onChange={handleFileChange}
              />
              {preview ? (
                <div className="item-ref-preview">
                  <div className="item-ref-img-wrap">
                    <img src={preview} alt="referencia" className="item-ref-thumb" />
                    {uploading && <div className="item-ref-overlay">Subiendo...</div>}
                  </div>
                  <div className="item-ref-actions">
                    <span className="item-ref-label">Foto de referencia</span>
                    <div className="item-ref-btns">
                      <button className="btn-ref replace" onClick={() => fileRef.current.click()} disabled={uploading}>
                        <Upload size={12} /> Reemplazar
                      </button>
                      <button className="btn-ref remove" onClick={handleEliminarFoto} disabled={uploading}>
                        <X size={12} /> Quitar
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <button className="item-ref-upload-btn" onClick={() => fileRef.current.click()} disabled={uploading}>
                  <Image size={14} />
                  <span>Agregar foto de referencia</span>
                </button>
              )}
            </div>
          )}

          <button
            className="btn-save-config"
            onClick={handleSaveConfig}
            disabled={savingConfig}
          >
            {savingConfig ? "Guardando..." : "Guardar configuración"}
          </button>
        </div>
      ) : (
        // ── Configuración Convencional ──
        <div className="item-conv-config">
          <label className="permite-foto-label">
            <input
              type="checkbox"
              checked={item.permite_foto}
              onChange={async (e) => {
                await checklistsAPI.actualizarItem(item.id, { permite_foto: e.target.checked });
                onRefrescar();
              }}
            />
            <span>Permitir foto opcional al operario</span>
          </label>
        </div>
      )}
    </div>
  );
}