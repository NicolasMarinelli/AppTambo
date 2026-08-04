import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Login from "./pages/Login";
import Register from "./pages/Register";
import SupervisorLayout from "./pages/supervisor/SupervisorLayout";
import Dashboard from "./pages/supervisor/Dashboard";
import Checklists from "./pages/supervisor/Checklists";
import ChecklistDetalle from "./pages/supervisor/ChecklistDetalle";
import Notificaciones from "./pages/supervisor/Notificaciones";
import OperarioLayout from "./pages/operario/OperarioLayout";
import Pendientes from "./pages/operario/Pendientes";
import Checklist from "./pages/operario/Checklist";
import Equipo from "./pages/supervisor/Equipo";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          <Route
            path="/supervisor"
            element={
              <ProtectedRoute rol="supervisor">
                <SupervisorLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="checklists" element={<Checklists />} />
            <Route path="checklists/:id" element={<ChecklistDetalle />} />
            <Route path="notificaciones" element={<Notificaciones />} />
            <Route path="equipo" element={<Equipo />} />
          </Route>

          <Route
            path="/operario"
            element={
              <ProtectedRoute rol="operario">
                <OperarioLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Pendientes />} />
            <Route path="checklist/:id" element={<Checklist />} />
          </Route>

          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}