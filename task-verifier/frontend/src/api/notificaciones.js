import client from "./client";

export const notificacionesAPI = {
  listar: (soloNoLeidas = false) =>
    client.get(`/notificaciones${soloNoLeidas ? "?solo_no_leidas=true" : ""}`),
  count: () => client.get("/notificaciones/count"),
  detalle: (id) => client.get(`/notificaciones/${id}`),
  marcarLeida: (id) => client.patch(`/notificaciones/${id}/leer`),
  marcarTodasLeidas: () => client.patch("/notificaciones/leer-todas"),
};