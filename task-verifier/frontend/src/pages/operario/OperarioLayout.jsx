import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { ClipboardCheck, LogOut } from "lucide-react";
import "./Operario.css";

export default function OperarioLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => { logout(); navigate("/login"); };

  return (
    <div className="op-shell">
      <header className="op-header">
        <div className="op-header-left">
          <div className="op-logo-icon"><ClipboardCheck size={18} /></div>
          <span className="op-logo-text">TaskVerifier</span>
        </div>
        <nav className="op-nav">
          <NavLink to="/operario" end className={({ isActive }) => `op-nav-item ${isActive ? "active" : ""}`}>
            Mis tareas
          </NavLink>
        </nav>
        <div className="op-header-right">
          <div className="op-user">
            <div className="op-avatar">{user?.nombre?.charAt(0).toUpperCase()}</div>
            <span className="op-user-name">{user?.nombre}</span>
          </div>
          <button className="op-logout" onClick={handleLogout} title="Cerrar sesión">
            <LogOut size={16} />
          </button>
        </div>
      </header>
      <main className="op-main">
        <Outlet />
      </main>
    </div>
  );
}