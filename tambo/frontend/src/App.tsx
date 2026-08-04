import { Route, Routes } from "react-router-dom";

import { CowHeadIcon } from "./components/CowHeadIcon";
import { NavMenu } from "./components/NavMenu";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { useAuth } from "./context/AuthContext";
import { AdminUsersPage } from "./pages/AdminUsersPage";
import { CalfRecordFormPage } from "./pages/CalfRecordFormPage";
import { CalfRecordsListPage } from "./pages/CalfRecordsListPage";
import { LoginPage } from "./pages/LoginPage";

function Layout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      <header className="app-header">
        {user && <NavMenu user={user} onLogout={logout} />}
        <div className="brand">
          <CowHeadIcon size={26} />
          <h1>Nacimientos de Terneros</h1>
        </div>
      </header>
      <main>{children}</main>
    </div>
  );
}

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <CalfRecordsListPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/nuevo"
          element={
            <ProtectedRoute allowedRoles={["admin", "operario"]}>
              <CalfRecordFormPage mode="create" />
            </ProtectedRoute>
          }
        />
        <Route
          path="/editar/:id"
          element={
            <ProtectedRoute allowedRoles={["admin", "operario"]}>
              <CalfRecordFormPage mode="edit" />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/usuarios"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <AdminUsersPage />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Layout>
  );
}
