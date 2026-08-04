export function getFotoUrl(url) {
  if (!url) return null;
  // Si ya es una URL completa (Cloudinary), usarla directamente
  if (url.startsWith("http")) return url;
  // Si es una ruta local (desarrollo anterior), agregar el base
  return `http://localhost:8000${url}`;
}