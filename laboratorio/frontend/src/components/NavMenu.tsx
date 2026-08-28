import { useEffect, useRef, useState } from "react";
import { NavLink } from "react-router-dom";

import type { User } from "../api/types";

interface NavMenuProps {
  user: User;
  onLogout: () => void;
}

export function NavMenu({ user, onLogout }: NavMenuProps) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;

    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [open]);

  function close() {
    setOpen(false);
  }

  return (
    <div className="nav-menu" ref={containerRef}>
      <button
        type="button"
        className="hamburger-btn"
        aria-label="Abrir menú"
        aria-expanded={open}
        onClick={() => setOpen((v) => !v)}
      >
        <span />
        <span />
        <span />
      </button>

      {open && (
        <div className="nav-drawer">
          <div className="nav-drawer-user">
            {user.username} <span className="nav-drawer-role">({user.role})</span>
          </div>
          <NavLink to="/" end onClick={close}>
            Nuevo análisis
          </NavLink>
          <NavLink to="/admin" onClick={close}>
            Tipos de análisis y fotos modelo
          </NavLink>
          <button
            className="nav-drawer-logout"
            onClick={() => {
              close();
              onLogout();
            }}
          >
            Salir
          </button>
        </div>
      )}
    </div>
  );
}
