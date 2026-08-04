import client from "./client";

export const operarioAPI = {
  pendientes: () => client.get("/operario/pendientes"),
  responder: (itemId, foto) => {
    const form = new FormData();
    form.append("item_id", itemId);
    form.append("foto", foto);
    return client.post("/operario/responder", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  historialItem: (itemId) => client.get(`/operario/respuestas/${itemId}`),
  responderConvencional: (itemId, texto, foto = null) => {
  const form = new FormData();
  form.append("item_id", itemId);
  form.append("texto", texto);
  if (foto) form.append("foto", foto);
  return client.post("/operario/responder-convencional", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
},
};

