// In-memory only, deliberadamente no persistido en localStorage/sessionStorage
// (mismo criterio que tambo/frontend/src/api/tokenStore.ts) para que un XSS
// no pueda leer el JWT del disco. Se pierde al refrescar la página; el
// usuario simplemente vuelve a loguearse.
let token: string | null = null;

export function getToken(): string | null {
  return token;
}

export function setToken(next: string | null): void {
  token = next;
}
