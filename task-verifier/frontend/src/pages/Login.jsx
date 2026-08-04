import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Auth.css";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
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
      const user = await login(form.email, form.password);
      navigate(user.rol === "supervisor" ? "/supervisor" : "/operario");
    } catch (err) {
      setError(err.response?.data?.detail || "Error al iniciar sesión");
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
        <div className="auth-features">
          <div className="feature">
            <span className="feature-icon">📸</span>
            <span>Verificación por foto en tiempo real</span>
          </div>
          <div className="feature">
            <span className="feature-icon">🤖</span>
            <span>Análisis automático con IA</span>
          </div>
          <div className="feature">
            <span className="feature-icon">🔔</span>
            <span>Notificaciones instantáneas</span>
          </div>
        </div>
      </div>

      <div className="auth-right">
        <div className="auth-card">
          <div className="auth-header">
            <h2>Bienvenido de vuelta</h2>
            <p>Ingresá a tu cuenta para continuar</p>
          </div>

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="field">
              <label>Email</label>
              <input
                type="email"
                name="email"
                value={form.email}
                onChange={handleChange}
                placeholder="tu@empresa.com"
                required
                autoComplete="email"
              />
            </div>

            <div className="field">
              <label>Contraseña</label>
              <input
                type="password"
                name="password"
                value={form.password}
                onChange={handleChange}
                placeholder="••••••••"
                required
                autoComplete="current-password"
              />
            </div>

            {error && <div className="auth-error">{error}</div>}

            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? <span className="spinner" /> : "Ingresar"}
            </button>
          </form>

          <div className="auth-footer">
            ¿No tenés cuenta?{" "}
            <Link to="/register">Registrate</Link>
          </div>
        </div>
      </div>
    </div>
  );
}