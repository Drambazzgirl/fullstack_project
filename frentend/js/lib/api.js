const API_BASE = '/api';

function getToken() {
  return localStorage.getItem('access_token');
}

async function request(path, options = {}) {
  const headers = options.headers || {};
  if (!options.body) headers['Content-Type'] = 'application/json';
  const token = getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(API_BASE + path, { ...options, headers });
  if (!res.ok) {
    const text = await res.text();
    let json;
    try { json = JSON.parse(text); } catch (e) { json = { detail: text }; }
    const err = new Error(json.detail || res.statusText);
    err.status = res.status;
    err.body = json;
    throw err;
  }

  if (res.status === 204) return null;
  return res.json();
}

export async function getComplaints({ department, status } = {}) {
  const params = new URLSearchParams();
  if (department) params.set('department', department);
  if (status) params.set('status_filter', status);
  const q = params.toString();
  return request(`/complaints${q ? '?' + q : ''}`);
}

export async function getComplaint(id) {
  return request(`/complaints/${id}`);
}

export async function markInProgress(id) {
  return request(`/admin/cm-admin/complaints/${id}/in-progress`, { method: 'PUT' });
}

export async function markSolved(id, admin_response) {
  const body = admin_response ? JSON.stringify({ admin_response }) : undefined;
  return request(`/admin/complaints/${id}/solve`, { method: 'PUT', body });
}

export async function addMessage(id, message) {
  return request(`/admin/cm-admin/complaints/${id}/messages`, { method: 'POST', body: JSON.stringify({ message }) });
}

export async function getMessagesForComplaintAsCAdmin(id, sender_role) {
  const params = new URLSearchParams();
  if (sender_role) params.set('sender_role', sender_role);
  const q = params.toString();
  return request(`/admin/c-admin/complaints/${id}/messages${q ? '?' + q : ''}`);
}

export async function getProfile() {
  return request('/auth/me');
}