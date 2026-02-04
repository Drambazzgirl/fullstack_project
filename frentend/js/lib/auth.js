export function saveToken(token) {
  localStorage.setItem('access_token', token);
}

export function getToken() {
  return localStorage.getItem('access_token');
}

export function removeToken() {
  localStorage.removeItem('access_token');
}

export function parseJwt(token) {
  if (!token) return null;
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    const payload = parts[1];
    // add padding
    const b64 = payload.replace(/-/g, '+').replace(/_/g, '/');
    const padded = b64 + '='.repeat((4 - (b64.length % 4)) % 4);
    const json = atob(padded);
    return JSON.parse(json);
  } catch (e) {
    console.error('parseJwt error', e);
    return null;
  }
}

export async function getProfile() {
  // uses API helper directly to avoid duplication
  const token = getToken();
  if (!token) return null;
  try {
    const res = await fetch('/api/auth/me', { headers: { Authorization: `Bearer ${token}` } });
    if (!res.ok) throw new Error('Unauthorized');
    return res.json();
  } catch (e) {
    console.warn('Could not fetch profile', e);
    return null;
  }
}