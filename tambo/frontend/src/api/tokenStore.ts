// In-memory only, deliberately not persisted to localStorage/sessionStorage
// so a stolen XSS payload can't read the JWT off disk. Lost on page refresh
// by design; the user just logs in again.
let token: string | null = null;

export function getToken(): string | null {
  return token;
}

export function setToken(next: string | null): void {
  token = next;
}
