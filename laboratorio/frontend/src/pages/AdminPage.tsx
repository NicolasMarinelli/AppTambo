import { useEffect, useState, type FormEvent } from "react";

import { apiClient } from "../api/client";
import type { EtiquetaFoto, FotoReferencia, TipoAnalisis } from "../api/types";

// Una sola pantalla: alta/edición de tipos de análisis + gestión de sus
// fotos modelo (aprobado/rechazado). Accesible para admin y laboratorio
// (ver App.tsx) — quien mejor conoce cómo se ve un cultivo bien o mal es
// el propio personal de laboratorio, no solo el admin.
export function AdminPage() {
  const [tipos, setTipos] = useState<TipoAnalisis[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [fotos, setFotos] = useState<FotoReferencia[]>([]);

  const [nombre, setNombre] = useState("");
  const [slug, setSlug] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [criterios, setCriterios] = useState("");
  const [errorTipo, setErrorTipo] = useState<string | null>(null);

  const [file, setFile] = useState<File | null>(null);
  const [etiqueta, setEtiqueta] = useState<EtiquetaFoto>("aprobado");
  const [descripcionFoto, setDescripcionFoto] = useState("");
  const [errorFoto, setErrorFoto] = useState<string | null>(null);

  async function fetchTipos() {
    const { data } = await apiClient.get<TipoAnalisis[]>("/tipos-analisis", { params: { incluir_inactivos: true } });
    setTipos(data);
  }

  async function fetchFotos(tipoId: number) {
    const { data } = await apiClient.get<FotoReferencia[]>(`/tipos-analisis/${tipoId}/fotos-referencia`, {
      params: { incluir_inactivas: true },
    });
    setFotos(data);
  }

  useEffect(() => {
    fetchTipos();
  }, []);

  useEffect(() => {
    if (selectedId) fetchFotos(selectedId);
  }, [selectedId]);

  async function handleCreateTipo(event: FormEvent) {
    event.preventDefault();
    setErrorTipo(null);
    try {
      await apiClient.post("/tipos-analisis", {
        nombre,
        slug,
        descripcion: descripcion || null,
        criterios_ia: criterios,
      });
      setNombre("");
      setSlug("");
      setDescripcion("");
      setCriterios("");
      fetchTipos();
    } catch {
      setErrorTipo("No se pudo crear. ¿El slug ya existe?");
    }
  }

  async function toggleActivo(tipo: TipoAnalisis) {
    await apiClient.put(`/tipos-analisis/${tipo.id}`, { activo: !tipo.activo });
    fetchTipos();
  }

  async function handleUploadFoto(event: FormEvent) {
    event.preventDefault();
    if (!selectedId || !file) return;
    setErrorFoto(null);
    try {
      const formData = new FormData();
      formData.append("etiqueta", etiqueta);
      if (descripcionFoto) formData.append("descripcion", descripcionFoto);
      formData.append("file", file);
      await apiClient.post(`/tipos-analisis/${selectedId}/fotos-referencia`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setFile(null);
      setDescripcionFoto("");
      fetchFotos(selectedId);
    } catch {
      setErrorFoto("No se pudo subir la foto.");
    }
  }

  async function deactivateFoto(fotoId: number) {
    if (!selectedId) return;
    await apiClient.delete(`/tipos-analisis/${selectedId}/fotos-referencia/${fotoId}`);
    fetchFotos(selectedId);
  }

  const selected = tipos.find((t) => t.id === selectedId) ?? null;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
      <section>
        <h2>Tipos de análisis</h2>
        <div className="card">
          <h3>Nuevo tipo de análisis</h3>
          <form className="form-grid" onSubmit={handleCreateTipo}>
            <label>
              Nombre
              <input value={nombre} onChange={(e) => setNombre(e.target.value)} required />
            </label>
            <label>
              Slug
              <input value={slug} onChange={(e) => setSlug(e.target.value)} placeholder="ej. mastitis" required />
            </label>
            <label className="full-width">
              Descripción (opcional)
              <input value={descripcion} onChange={(e) => setDescripcion(e.target.value)} />
            </label>
            <label className="full-width">
              Criterios para la IA
              <textarea
                value={criterios}
                onChange={(e) => setCriterios(e.target.value)}
                rows={3}
                required
                placeholder="Qué tiene que mirar la IA para aprobar o rechazar la muestra"
              />
            </label>
            {errorTipo && <p className="form-error full-width">{errorTipo}</p>}
            <div className="full-width">
              <button type="submit" className="btn-primary">
                Crear tipo de análisis
              </button>
            </div>
          </form>
        </div>

        <div className="table-scroll" style={{ marginTop: "1.25rem" }}>
          <table>
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Slug</th>
                <th>Estado</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {tipos.map((tipo) => (
                <tr
                  key={tipo.id}
                  onClick={() => setSelectedId(tipo.id)}
                  style={{ cursor: "pointer", fontWeight: tipo.id === selectedId ? 700 : 400 }}
                >
                  <td>{tipo.nombre}</td>
                  <td>{tipo.slug}</td>
                  <td>{tipo.activo ? "Activo" : "Inactivo"}</td>
                  <td>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleActivo(tipo);
                      }}
                    >
                      {tipo.activo ? "Desactivar" : "Activar"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {selected && (
        <section>
          <h2>Fotos modelo — {selected.nombre}</h2>
          <div className="card">
            <h3>Nueva foto de referencia</h3>
            <form className="form-grid" onSubmit={handleUploadFoto}>
              <label>
                Etiqueta
                <select value={etiqueta} onChange={(e) => setEtiqueta(e.target.value as EtiquetaFoto)}>
                  <option value="aprobado">Aprobado (así se ve bien)</option>
                  <option value="rechazado">Rechazado (así se ve mal)</option>
                </select>
              </label>
              <label>
                Foto
                <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files?.[0] ?? null)} required />
              </label>
              <label className="full-width">
                Descripción (opcional)
                <input value={descripcionFoto} onChange={(e) => setDescripcionFoto(e.target.value)} />
              </label>
              {errorFoto && <p className="form-error full-width">{errorFoto}</p>}
              <div className="full-width">
                <button type="submit" className="btn-primary" disabled={!file}>
                  Subir foto
                </button>
              </div>
            </form>
          </div>

          <div
            style={{
              display: "grid",
              gap: "1rem",
              gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))",
              marginTop: "1.25rem",
            }}
          >
            {fotos.map((foto) => (
              <div key={foto.id} className="card" style={{ opacity: foto.activo ? 1 : 0.5 }}>
                <img
                  src={foto.imagen_url}
                  alt={foto.etiqueta}
                  style={{ width: "100%", height: "120px", objectFit: "cover", borderRadius: "var(--radius-md)" }}
                />
                <span
                  className="badge"
                  style={{
                    marginTop: "0.5rem",
                    background: foto.etiqueta === "aprobado" ? "var(--color-primary)" : "#b3261e",
                  }}
                >
                  {foto.etiqueta}
                </span>
                {foto.activo && (
                  <div>
                    <button style={{ marginTop: "0.5rem" }} onClick={() => deactivateFoto(foto.id)}>
                      Desactivar
                    </button>
                  </div>
                )}
              </div>
            ))}
            {fotos.length === 0 && <p>Todavía no hay fotos de referencia para este tipo de análisis.</p>}
          </div>
        </section>
      )}
    </div>
  );
}
