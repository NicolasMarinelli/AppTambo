import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { checklistsAPI } from "../../api/checklists";
import { Plus, Trash2, Eye, ClipboardList } from "lucide-react";
import Badge from "../../components/Badge";

const FRECUENCIAS = ["diaria", "semanal", "mensual", "unica"];

export default function Checklists() {
  const navigate = useNavigate();
  const [checklists, setChecklists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
  nombre: "",
  descripcion: "",
  frecuencia: "diaria",
  tipo: "ia",        // ← nuevo
  items: []
});
  const [nuevoItem, setNuevoItem] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    cargar();
  }, []);

  const cargar = async () => {
    setLoading(true);
    const { data } = await checklistsAPI.listar();
    setChecklists(data);
    setLoading(false);
  };

  const agregarItemLocal = () => {
    if (!nuevoItem.trim()) return;
    setForm({
      ...form,
      items: [...form.items, { pregunta: nuevoItem.trim(), orden: form.items.length }],
    });
    setNuevoItem("");
  };

  const quitarItemLocal = (idx) => {
    setForm({ ...form, items: form.items.filter((_, i) => i !== idx) });
  };

  const handleCrear = async (e) => {
    e.preventDefault();
    if (form.items.length === 0) { setError("Agregá al menos un ítem"); return; }
    setSaving(true);
    setError("");
    try {
      await checklistsAPI.crear(form);
      setShowForm(false);
      setForm({ nombre: "", descripcion: "", frecuencia: "diaria", items: [] });
      cargar();
    } catch (err) {
      setError(err.response?.data?.detail || "Error al crear");
    } finally {
      setSaving(false);
    }
  };

  const handleEliminar = async (id, e) => {
    e.stopPropagation();
    if (!confirm("¿Eliminar este checklist?")) return;
    await checklistsAPI.eliminar(id);
    cargar();
  };

  const frecBadge = { diaria: "info", semanal: "success", mensual: "warning", unica: "default" };

  if (loading) return <div className="sup-loading">Cargando...</div>;

  return (
    <div className="sup-page">
      <div className="sup-page-header">
        <div>
          <h1>Checklists</h1>
          <p>{checklists.length} checklists creados</p>
        </div>
        <button className="btn-accent" onClick={() => setShowForm(true)}>
          <Plus size={16} /> Nuevo checklist
        </button>
      </div>

      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Nuevo checklist</h3>
            <form onSubmit={handleCrear} className="modal-form">
              <div className="field">
                <label>Nombre</label>
                <input
                  value={form.nombre}
                  onChange={(e) => setForm({ ...form, nombre: e.target.value })}
                  placeholder="Ej: Limpieza de maquinaria"
                  required
                />
              </div>
              <div className="field">
                <label>Descripción (opcional)</label>
                <input
                  value={form.descripcion}
                  onChange={(e) => setForm({ ...form, descripcion: e.target.value })}
                  placeholder="Descripción breve"
                />
              </div>
              <div className="field">
                <label>Frecuencia</label>
                <select
                  value={form.frecuencia}
                  onChange={(e) => setForm({ ...form, frecuencia: e.target.value })}
                >
                  {FRECUENCIAS.map((f) => (
                    <option key={f} value={f}>{f.charAt(0).toUpperCase() + f.slice(1)}</option>
                  ))}
                </select>
              </div>
              <div className="field">
              <label>Tipo de checklist</label>
              <div className="tipo-checklist-selector">
                <button
                  type="button"
                  className={`tipo-cl-btn ${form.tipo === "ia" ? "active" : ""}`}
                  onClick={() => setForm({ ...form, tipo: "ia" })}
                >
                  <span className="tipo-cl-icon">🤖</span>
                  <span className="tipo-cl-label">Con IA</span>
                  <span className="tipo-cl-desc">Verifica fotos automáticamente</span>
                </button>
                <button
                  type="button"
                  className={`tipo-cl-btn ${form.tipo === "convencional" ? "active" : ""}`}
                  onClick={() => setForm({ ...form, tipo: "convencional" })}
                >
                  <span className="tipo-cl-icon">✓</span>
                  <span className="tipo-cl-label">Convencional</span>
                  <span className="tipo-cl-desc">Checkbox y texto libre</span>
                </button>
              </div>
            </div>

              <div className="field">
                <label>Ítems</label>
                <div className="item-input-row">
                  <input
                    value={nuevoItem}
                    onChange={(e) => setNuevoItem(e.target.value)}
                    placeholder="Ej: ¿La máquina está apagada?"
                    onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), agregarItemLocal())}
                  />
                  <button type="button" className="btn-add-item" onClick={agregarItemLocal}>
                    <Plus size={16} />
                  </button>
                </div>
                {form.items.length > 0 && (
                  <div className="items-preview">
                    {form.items.map((item, i) => (
                      <div key={i} className="item-preview-row">
                        <span className="item-num">{i + 1}</span>
                        <span className="item-text">{item.pregunta}</span>
                        <button type="button" onClick={() => quitarItemLocal(i)}>
                          <Trash2 size={13} />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {error && <div className="form-error">{error}</div>}

              <div className="modal-actions">
                <button type="button" className="btn-ghost" onClick={() => setShowForm(false)}>
                  Cancelar
                </button>
                <button type="submit" className="btn-accent" disabled={saving}>
                  {saving ? "Guardando..." : "Crear checklist"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {checklists.length === 0 ? (
        <div className="sup-empty-state">
          <ClipboardList size={48} strokeWidth={1} />
          <p>Todavía no creaste ningún checklist.</p>
          <button className="btn-accent" onClick={() => setShowForm(true)}>
            <Plus size={16} /> Crear el primero
          </button>
        </div>
      ) : (
        <div className="checklist-grid">
          {checklists.map((c) => (
            <div key={c.id} className="checklist-card" onClick={() => navigate(`/supervisor/checklists/${c.id}`)}>
              <div className="checklist-card-header">
                <div className="checklist-card-title">{c.nombre}</div>
                <button
                  className="btn-icon danger"
                  onClick={(e) => handleEliminar(c.id, e)}
                  title="Eliminar"
                >
                  <Trash2 size={14} />
                </button>
              </div>
              {c.descripcion && <div className="checklist-card-desc">{c.descripcion}</div>}
              <div className="checklist-card-footer">
                <Badge variant={frecBadge[c.frecuencia]}>{c.frecuencia}</Badge>
                <span className="checklist-items-count">{c.total_items} ítems</span>
                <Eye size={14} color="#8892a4" />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}