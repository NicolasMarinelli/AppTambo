import { useState, type FormEvent } from "react";
import axios from "axios";
import { Navigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

export function LoginPage() {
  const { user, login, isLoading } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  if (user) {
    return <Navigate to="/" replace />;
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      await login(username, password);
    } catch (err) {
      const status = axios.isAxiosError(err) ? err.response?.status : undefined;
      setError(status === 403 ? "Tu usuario no tiene acceso a laboratorio." : "Usuario o contraseña incorrectos");
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-hero">
          <div>
            <h2 style={{ marginBottom: "0.5rem" }}>🧪 Laboratorio</h2>
            <p style={{ color: "var(--color-text-muted)", fontSize: "0.9rem" }}>
              Evaluación de cultivos con ayuda de IA
            </p>
          </div>
        </div>
        <form className="login-form" onSubmit={handleSubmit}>
          <h1>Ingresar</h1>
          <p className="subtitle">Usá el mismo usuario y contraseña que en tambo.</p>
          <label>
            Usuario
            <input value={username} onChange={(e) => setUsername(e.target.value)} autoFocus required />
          </label>
          <label>
            Contraseña
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </label>
          {error && <p className="form-error">{error}</p>}
          <button type="submit" className="btn-primary" disabled={isLoading}>
            {isLoading ? "Ingresando..." : "Ingresar"}
          </button>
        </form>
      </div>
    </div>
  );
}
