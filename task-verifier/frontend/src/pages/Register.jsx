import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Auth.css";

const PLANES = [
  {
    id: "basico",
    nombre: "Básico",
    creditos: "1.000 créditos/mes",
    precio: "A definir",
    features: ["Hasta 1.000 análisis IA por mes", "Operarios ilimitados", "Soporte estándar"],
  },
  {
    id: "premium",
    nombre: "Premium",
    creditos: "5.000 créditos/mes",
    precio: "A definir",
    features: ["Hasta 5.000 análisis IA por mes", "Operarios ilimitados", "Soporte prioritario"],
  },
];

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [tipo, setTipo] = useState("empresa"); // empresa | codigo
  const [form, setForm] = useState({
    nombre: "",
    email: "",
    password: "",
    nombre_empresa: "",
    plan: "basico",
    codigo_invitacion: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const payload = {
        nombre: form.nombre,
        email: form.email,
        password: form.password,
        ...(tipo === "empresa"
          ? { nombre_empresa: form.nombre_empresa, plan: form.plan }
          : { codigo_invitacion: form.codigo_invitacion }),
      };
      const user = await register(payload);
      navigate(user.rol === "supervisor" ? "/supervisor" : "/operario");
    } catch (err) {
      setError(err.response?.data?.detail || "Error al registrarse");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-left">
        <div className="auth-brand">
          <div className="brand-icon">✓</div>
          <h1>TaskVerifier</h1>
          <p>Verificación inteligente de tareas con IA</p>
        </div>
        <div className="planes-preview">
          {PLANES.map((plan) => (
            <div
              key={plan.id}
              className={`plan-card ${form.plan === plan.id && tipo === "empresa" ? "active" : ""}`}
            >
              <div className="plan-nombre">{plan.nombre}</div>
              <div className="plan-creditos">{plan.creditos}</div>
              <ul className="plan-features">
                {plan.features.map((f) => (
                  <li key={f}>✓ {f}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      <div className="auth-right">
        <div className="auth-card">
          <div className="auth-header">
            <h2>Crear cuenta</h2>
            <p>¿Cómo querés registrarte?</p>
          </div>

          <div className="tipo-selector">
            <button
              type="button"
              className={`tipo-btn ${tipo === "empresa" ? "active" : ""}`}
              onClick={() => setTipo("empresa")}
            >
              Nueva empresa
            </button>
            <button
              type="button"
              className={`tipo-btn ${tipo === "codigo" ? "active" : ""}`}
              onClick={() => setTipo("codigo")}
            >
              Tengo un código
            </button>
          </div>

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="field">
              <label>Tu nombre</label>
              <input
                name="nombre"
                value={form.nombre}
                onChange={handleChange}
                placeholder="Juan García"
                required
              />
            </div>

            <div className="field">
              <label>Email</label>
              <input
                type="email"
                name="email"
                value={form.email}
                onChange={handleChange}
                placeholder="tu@empresa.com"
                required
              />
            </div>

            <div className="field">
              <label>Contraseña</label>
              <input
                type="password"
                name="password"
                value={form.password}
                onChange={handleChange}
                placeholder="Mínimo 6 caracteres"
                required
                minLength={6}
              />
            </div>

            {tipo === "empresa" ? (
              <>
                <div className="field">
                  <label>Nombre de tu empresa</label>
                  <input
                    name="nombre_empresa"
                    value={form.nombre_empresa}
                    onChange={handleChange}
                    placeholder="Ej: Industrias García S.A."
                    required
                  />
                </div>
                <div className="field">
                  <label>Plan</label>
                  <div className="plan-selector">
                    {PLANES.map((plan) => (
                      <button
                        key={plan.id}
                        type="button"
                        className={`plan-option ${form.plan === plan.id ? "active" : ""}`}
                        onClick={() => setForm({ ...form, plan: plan.id })}
                      >
                        <span className="plan-option-nombre">{plan.nombre}</span>
                        <span className="plan-option-cred">{plan.creditos}</span>
                      </button>
                    ))}
                  </div>
                </div>
              </>
            ) : (
              <div className="field">
                <label>Código de invitación</label>
                <input
                  name="codigo_invitacion"
                  value={form.codigo_invitacion}
                  onChange={handleChange}
                  placeholder="Ej: abc123xyz..."
                  required
                />
              </div>
            )}

            {error && <div className="auth-error">{error}</div>}

            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? <span className="spinner" /> : "Crear cuenta"}
            </button>
          </form>

          <div className="auth-footer">
            ¿Ya tenés cuenta? <Link to="/login">Iniciá sesión</Link>
          </div>
        </div>
      </div>
    </div>
  );
}