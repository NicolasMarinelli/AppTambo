import { useState, type FormEvent } from "react";
import { Navigate } from "react-router-dom";

import { CowHero } from "../components/CowHero";
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
    } catch {
      setError("Usuario o contraseña incorrectos");
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-hero">
          <CowHero />
        </div>
        <form className="login-form" onSubmit={handleSubmit}>
          <h1>Nacimientos de Terneros</h1>
          <p className="subtitle">Gestión de partos, caravanas y calostrado del establecimiento.</p>
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
