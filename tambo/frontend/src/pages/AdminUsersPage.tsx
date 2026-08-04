import { useEffect, useState, type FormEvent } from "react";

import { apiClient } from "../api/client";
import type { User, UserRole } from "../api/types";

const ROLE_LABELS: Record<UserRole, string> = {
  admin: "Administrador",
  operario: "Operario",
  laboratorio: "Laboratorio",
};

export function AdminUsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<UserRole>("operario");
  const [error, setError] = useState<string | null>(null);

  async function fetchUsers() {
    const { data } = await apiClient.get<User[]>("/users");
    setUsers(data);
  }

  useEffect(() => {
    fetchUsers();
  }, []);

  async function handleCreate(event: FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      await apiClient.post("/users", { username, password, role, is_active: true });
      setUsername("");
      setPassword("");
      setRole("operario");
      fetchUsers();
    } catch {
      setError("No se pudo crear el usuario. ¿Ya existe ese nombre de usuario?");
    }
  }

  async function toggleActive(user: User) {
    await apiClient.put(`/users/${user.id}`, { is_active: !user.is_active });
    fetchUsers();
  }

  async function changeRole(user: User, newRole: UserRole) {
    await apiClient.put(`/users/${user.id}`, { role: newRole });
    fetchUsers();
  }

  return (
    <div>
      <h2>Gestión de usuarios</h2>

      <div className="card">
        <h3>Nuevo usuario</h3>
        <form className="form-grid" onSubmit={handleCreate}>
          <label>
            Usuario
            <input value={username} onChange={(e) => setUsername(e.target.value)} required />
          </label>
          <label>
            Contraseña
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6} />
          </label>
          <label>
            Rol
            <select value={role} onChange={(e) => setRole(e.target.value as UserRole)}>
              {Object.entries(ROLE_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </label>
          {error && <p className="form-error full-width">{error}</p>}
          <div className="full-width">
            <button type="submit" className="btn-primary">
              Crear usuario
            </button>
          </div>
        </form>
      </div>

      <div className="table-scroll" style={{ marginTop: "1.5rem" }}>
      <table>
        <thead>
          <tr>
            <th>Usuario</th>
            <th>Rol</th>
            <th>Estado</th>
            <th>Creado</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id}>
              <td>{user.username}</td>
              <td>
                <select value={user.role} onChange={(e) => changeRole(user, e.target.value as UserRole)}>
                  {Object.entries(ROLE_LABELS).map(([value, label]) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </select>
              </td>
              <td>{user.is_active ? "Activo" : "Inactivo"}</td>
              <td>{new Date(user.created_at).toLocaleDateString()}</td>
              <td>
                <button onClick={() => toggleActive(user)}>
                  {user.is_active ? "Desactivar" : "Activar"}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      </div>
    </div>
  );
}
