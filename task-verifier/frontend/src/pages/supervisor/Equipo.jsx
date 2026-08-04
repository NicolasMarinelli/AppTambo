import { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import { equipoAPI } from "../../api/equipo";
import { Copy, Check, Users, Plus, RefreshCw } from "lucide-react";
import Badge from "../../components/Badge";

export default function Equipo() {
  const { user } = useAuth();
  const [codigos, setCodigos] = useState([]);
  const [miembros, setMiembros] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generando, setGenerando] = useState(false);
  const [copiado, setCopiado] = useState(null);
  const [rolSeleccionado, setRolSeleccionado] = useState("operario");

  useEffect(() => { cargar(); }, []);

  const cargar = async () => {
    setLoading(true);
    try {
      const [cods, miemb] = await Promise.all([
        user?.es_principal ? equipoAPI.listarCodigos() : Promise.resolve({ data: [] }),
        equipoAPI.listarMiembros(),
      ]);
      setCodigos(cods.data);
      setMiembros(miemb.data);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerar = async () => {
    setGenerando(true);
    try {
      await equipoAPI.generarCodigo(rolSeleccionado);
      cargar();
    } finally {
      setGenerando(false);
    }
  };

  const handleCopiar = async (codigo) => {
    await navigator.clipboard.writeText(codigo);
    setCopiado(codigo);
    setTimeout(() => setCopiado(null), 2000);
  };

  if (loading) return <div className="sup-loading">Cargando...</div>;

  return (
    <div className="sup-page">
      <div className="sup-page-header">
        <div>
          <h1>Equipo</h1>
          <p>{miembros.length} operario{miembros.length !== 1 ? "s" : ""} registrado{miembros.length !== 1 ? "s" : ""}</p>
        </div>
        {user?.es_principal && (
          <div className="equipo-actions">
            <select
              value={rolSeleccionado}
              onChange={(e) => setRolSeleccionado(e.target.value)}
              className="rol-select"
            >
              <option value="operario">Operario</option>
              <option value="supervisor">Supervisor</option>
            </select>
            <button
              className="btn-accent"
              onClick={handleGenerar}
              disabled={generando}
            >
              <Plus size={16} />
              {generando ? "Generando..." : "Generar código"}
            </button>
          </div>
        )}
      </div>

      {/* Operarios registrados */}
      <div className="sup-section">
        <h2>Operarios activos</h2>
        {miembros.length === 0 ? (
          <div className="sup-empty-state">
            <Users size={40} strokeWidth={1} />
            <p>Todavía no hay operarios registrados.</p>
            <p style={{ fontSize: "13px" }}>
              Generá un código de invitación y compartilo con tu equipo.
            </p>
          </div>
        ) : (
          <div className="miembros-grid">
            {miembros.map((m) => (
              <div key={m.id} className="miembro-card">
                <div className="miembro-avatar">
                  {m.nombre.charAt(0).toUpperCase()}
                </div>
                <div className="miembro-info">
                  <div className="miembro-nombre">{m.nombre}</div>
                  <div className="miembro-email">{m.email}</div>
                </div>
                <Badge variant="info">Operario</Badge>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Códigos de invitación — solo supervisor principal */}
      {user?.es_principal && (
        <div className="sup-section">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
            <h2>Códigos de invitación</h2>
            <button className="btn-ghost" onClick={cargar}>
              <RefreshCw size={14} /> Actualizar
            </button>
          </div>

          {codigos.length === 0 ? (
            <div className="sup-empty">
              Generá un código para invitar a tu equipo.
            </div>
          ) : (
            <div className="codigos-list">
              {codigos.map((c) => (
                <div key={c.id} className={`codigo-row ${c.usado ? "usado" : ""}`}>
                  <div className="codigo-info">
                    <Badge variant={c.rol_destino === "supervisor" ? "warning" : "info"}>
                      {c.rol_destino}
                    </Badge>
                    <code className="codigo-valor">{c.codigo}</code>
                  </div>
                  <div className="codigo-meta">
                    <span className="codigo-fecha">
                      {new Date(c.creado_en).toLocaleDateString("es-AR")}
                    </span>
                    {c.usado ? (
                      <Badge variant="default">Usado</Badge>
                    ) : (
                      <button
                        className="btn-copiar"
                        onClick={() => handleCopiar(c.codigo)}
                        title="Copiar código"
                      >
                        {copiado === c.codigo
                          ? <><Check size={13} /> Copiado</>
                          : <><Copy size={13} /> Copiar</>
                        }
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Mensaje para supervisores no principales */}
      {!user?.es_principal && (
        <div className="no-principal-msg">
          Solo el supervisor principal puede gestionar invitaciones.
        </div>
      )}
    </div>
  );
}