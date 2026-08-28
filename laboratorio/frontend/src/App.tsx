import type { ReactNode } from "react";
import { Route, Routes } from "react-router-dom";

import { NavMenu } from "./components/NavMenu";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { useAuth } from "./context/AuthContext";
import { AdminPage } from "./pages/AdminPage";
import { LoginPage } from "./pages/LoginPage";
import { ResultPage } from "./pages/ResultPage";
import { TipoAnalisisSelectPage } from "./pages/TipoAnalisisSelectPage";
import { UploadSamplePage } from "./pages/UploadSamplePage";

function Layout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      <header className="app-header">
        {user && <NavMenu user={user} onLogout={logout} />}
        <div className="brand">
          <h1>🧪 Laboratorio</h1>
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
              <TipoAnalisisSelectPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/muestra/:tipoId"
          element={
            <ProtectedRoute>
              <UploadSamplePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/resultados/:resultadoId"
          element={
            <ProtectedRoute>
              <ResultPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <ProtectedRoute allowedRoles={["admin", "laboratorio"]}>
              <AdminPage />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Layout>
  );
}
