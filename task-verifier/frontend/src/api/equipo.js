import client from "./client";

export const equipoAPI = {
  listarCodigos: () => client.get("/auth/empresa/codigos"),
  generarCodigo: (rol_destino) =>
    client.post(`/auth/empresa/codigos?rol_destino=${rol_destino}`),
  listarMiembros: () => client.get("/usuarios/operarios"),
};