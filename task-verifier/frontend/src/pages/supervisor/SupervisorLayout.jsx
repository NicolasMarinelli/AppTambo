import { useState, useEffect } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { notificacionesAPI } from "../../api/notificaciones";
import client from "../../api/client";
import {
  LayoutDashboard, ClipboardList, Bell, LogOut, Menu, X, CheckSquare, Users 
} from "lucide-react";
import "./Supervisor.css";

export default function SupervisorLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [noLeidas, setNoLeidas] = useState(0);
  const [empresaInfo, setEmpresaInfo] = useState(null);

  useEffect(() => {
    client.get("/auth/empresa/info")
    .then(({ data }) => setEmpresaInfo(data))
    .catch(() => {});
    notificacionesAPI.count()
      .then(({ data }) => setNoLeidas(data.no_leidas))
      .catch(() => {});
    // Polling cada 30 segundos
    const interval = setInterval(() => {
      notificacionesAPI.count()
        .then(({ data }) => setNoLeidas(data.no_leidas))
        .catch(() => {});
    }, 30000);
    return () => clearInterval(interval);

  }, []);

  const handleLogout = () => { logout(); navigate("/login"); };

  const navItems = [
    { to: "/supervisor", icon: <LayoutDashboard size={18} />, label: "Dashboard", end: true },
    { to: "/supervisor/checklists", icon: <ClipboardList size={18} />, label: "Checklists" },
    { to: "/supervisor/notificaciones", icon: <Bell size={18} />, label: "Notificaciones", badge: noLeidas },
    { to: "/supervisor/equipo", icon: <Users size={18} />, label: "Equipo" },
  ];

  return (
    <div className="sup-shell">
      {/* Sidebar */}
      <aside className={`sup-sidebar ${sidebarOpen ? "open" : "closed"}`}>
        <div className="sup-logo">
          <div className="sup-logo-icon">
            <CheckSquare size={20} />
          </div>
          {sidebarOpen && <span>TaskVerifier</span>}
        </div>

        <nav className="sup-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `sup-nav-item ${isActive ? "active" : ""}`
              }
            >
              {item.icon}
              {sidebarOpen && <span>{item.label}</span>}
              {item.badge > 0 && (
                <span className="sup-badge">{item.badge}</span>
              )}
            </NavLink>
          ))}
        </nav>
            {empresaInfo && sidebarOpen && (
              <div className="sup-creditos">
                <div className="sup-creditos-header">
                  <span className="sup-creditos-plan">Plan {empresaInfo.plan}</span>
                  <span className={`sup-creditos-estado ${empresaInfo.membresia_activa ? "activo" : "vencido"}`}>
                    {empresaInfo.membresia_activa ? "Activo" : "Vencido"}
                  </span>
                </div>
                <div className="sup-creditos-barra">
                  <div
                    className="sup-creditos-fill"
                    style={{
                      width: `${Math.min(100, (empresaInfo.creditos_disponibles / empresaInfo.creditos_mensuales) * 100)}%`
                    }}
                  />
                </div>
                <div className="sup-creditos-texto">
                  {empresaInfo.creditos_disponibles.toLocaleString()} / {empresaInfo.creditos_mensuales.toLocaleString()} créditos
                </div>
                <div className="sup-creditos-vence">
                  Vence en {empresaInfo.dias_restantes} días
                </div>
              </div>
            )}  
        <div className="sup-user">
          {sidebarOpen && (
            <div className="sup-user-info">
              <div className="sup-avatar">
                {user?.nombre?.charAt(0).toUpperCase()}
              </div>
              <div>
                <div className="sup-user-name">{user?.nombre}</div>
                <div className="sup-user-rol">Supervisor</div>
              </div>
            </div>
          )}
          <button className="sup-logout" onClick={handleLogout} title="Cerrar sesión">
            <LogOut size={16} />
          </button>
        </div>
      </aside>

      {/* Contenido principal */}
      <div className="sup-main">
        <header className="sup-topbar">
          <button
            className="sup-menu-btn"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </header>
        <main className="sup-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}