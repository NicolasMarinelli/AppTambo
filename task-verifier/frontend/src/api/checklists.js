import client from "./client";

export const checklistsAPI = {
  listar: () => client.get("/checklists"),
  crear: (data) => client.post("/checklists", data),
  obtener: (id) => client.get(`/checklists/${id}`),
  actualizar: (id, data) => client.patch(`/checklists/${id}`, data),
  eliminar: (id) => client.delete(`/checklists/${id}`),

  // Items
  agregarItem: (checklistId, data) =>
    client.post(`/checklists/${checklistId}/items`, data),
  actualizarItem: (itemId, data) =>
    client.patch(`/checklists/items/${itemId}`, data),
  eliminarItem: (itemId) =>
    client.delete(`/checklists/items/${itemId}`),

  // Asignaciones
  listarOperarios: () => client.get("/usuarios/operarios"),
  asignar: (checklistId, operarioId) =>
    client.post(`/checklists/${checklistId}/asignaciones`, { operario_id: operarioId }),
  desasignar: (checklistId, operarioId) =>
    client.delete(`/checklists/${checklistId}/asignaciones/${operarioId}`),
  listarAsignaciones: (checklistId) =>
    client.get(`/checklists/${checklistId}/asignaciones`),

  // Respuestas
  todasRespuestas: () => client.get("/checklists/respuestas/todas"),
  detalleRespuesta: (id) => client.get(`/checklists/respuestas/${id}`),
  darFeedback: (id, data) =>
    client.patch(`/checklists/respuestas/${id}/feedback`, data),
  estadisticasIA: () => client.get("/checklists/respuestas/estadisticas-ia"),

  // Foto de referencia
  subirFotoReferencia: (itemId, foto) => {
    const form = new FormData();
    form.append("foto", foto);
    return client.post(`/checklists/items/${itemId}/foto-referencia`, form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  eliminarFotoReferencia: (itemId) =>
    client.delete(`/checklists/items/${itemId}/foto-referencia`),

};

