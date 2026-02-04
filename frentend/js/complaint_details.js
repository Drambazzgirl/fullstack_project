import * as api from './lib/api.js';
import { getToken, parseJwt, getProfile } from './lib/auth.js';

function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  Object.entries(attrs).forEach(([k, v]) => {
    if (k === 'class') node.className = v;
    else if (k === 'text') node.textContent = v;
    else node.setAttribute(k, v);
  });
  children.forEach(c => node.appendChild(c));
  return node;
}

function getIdFromQuery() {
  return new URLSearchParams(window.location.search).get('id');
}

async function loadComplaint() {
  const id = getIdFromQuery();
  if (!id) return showError('Missing complaint id');

  try {
    const c = await api.getComplaint(id);
    renderComplaint(c);
    // If user is admin, load messages
    const token = getToken();
    if (token) {
      const p = await getProfile();
      if (p && (p.role_name === 'cm_admin' || p.role_name === 'c_admin')) {
        await loadMessages(id);
        // show admin controls
        showAdminControls(p, c);
      }
    }
  } catch (err) {
    console.error('Failed to load complaint', err);
    showError(err.body?.detail || err.message || 'Failed to load');
  }
}

function renderComplaint(c) {
  const container = document.getElementById('complaint-detail');
  container.innerHTML = '';

  container.appendChild(el('h2', { text: c.title }));
  container.appendChild(el('div', { class: 'meta', text: `${c.department} • ${new Date(c.created_at).toLocaleString()}` }));
  container.appendChild(el('p', { text: c.description }));

  if (c.image_url) {
    container.appendChild(el('img', { src: c.image_url, class: 'complaint-image', alt: c.title }));
  }
  if (c.voice_url) {
    const audio = el('audio', { controls: true });
    const src = el('source', { src: c.voice_url });
    audio.appendChild(src);
    container.appendChild(audio);
  }

  container.appendChild(el('div', { class: 'status', text: `Status: ${c.status}` }));

  const resp = el('div', { class: 'admin-response' });
  resp.appendChild(el('h4', { text: 'Admin Response' }));
  resp.appendChild(el('div', { text: c.admin_response || 'No response yet' }));
  container.appendChild(resp);
}

async function loadMessages(id) {
  try {
    const msgs = await api.getMessagesForComplaintAsCAdmin(id);
    renderMessages(msgs);
  } catch (err) {
    // silently ignore if not allowed to view messages
    console.debug('Messages not available', err);
  }
}

function renderMessages(msgs) {
  const container = document.getElementById('messages');
  if (!container) return;
  container.innerHTML = '';
  msgs.forEach(m => {
    const it = el('div', { class: 'message' });
    it.appendChild(el('div', { class: 'sender', text: m.sender_name || `User ${m.sender_id}` }));
    it.appendChild(el('div', { class: 'text', text: m.message }));
    it.appendChild(el('div', { class: 'created', text: new Date(m.created_at).toLocaleString() }));
    container.appendChild(it);
  });
}

function showAdminControls(profile, complaint) {
  const controls = document.getElementById('admin-controls');
  if (!controls) return;
  controls.innerHTML = '';

  if (profile.role_name === 'cm_admin') {
    const inProgressBtn = el('button', { class: 'btn', text: 'Mark In Progress' });
    inProgressBtn.addEventListener('click', async () => {
      try {
        await api.markInProgress(complaint.id);
        await loadComplaint();
        await loadMessages(complaint.id);
      } catch (err) { console.error(err); showError(err.body?.detail || err.message || 'Failed'); }
    });
    controls.appendChild(inProgressBtn);

    const msgBox = el('div', { class: 'msg-box' });
    const input = el('textarea', { placeholder: 'Add a message...' });
    const send = el('button', { class: 'btn', text: 'Send' });
    send.addEventListener('click', async () => {
      try {
        await api.addMessage(complaint.id, input.value);
        input.value = '';
        await loadMessages(complaint.id);
      } catch (err) { console.error(err); showError(err.body?.detail || err.message || 'Failed to send'); }
    });
    msgBox.appendChild(input);
    msgBox.appendChild(send);
    controls.appendChild(msgBox);
  }

  if (profile.role_name === 'c_admin') {
    const solveBtn = el('button', { class: 'btn btn-solve', text: 'Mark Solved' });
    const respInput = el('textarea', { placeholder: 'Optional resolution note' });
    solveBtn.addEventListener('click', async () => {
      try {
        await api.markSolved(complaint.id, respInput.value);
        await loadComplaint();
      } catch (err) { console.error(err); showError(err.body?.detail || err.message || 'Failed to solve'); }
    });
    controls.appendChild(respInput);
    controls.appendChild(solveBtn);
  }
}

function showError(msg) {
  const elErr = document.getElementById('error-msg');
  if (!elErr) return;
  elErr.textContent = msg;
  elErr.style.display = 'block';
  setTimeout(() => (elErr.style.display = 'none'), 5000);
}

// Polling to auto-refresh detail view
let pollHandle;

document.addEventListener('DOMContentLoaded', async () => {
  await loadComplaint();
  const id = getIdFromQuery();
  pollHandle = setInterval(() => loadComplaint(), 10000);

  window.addEventListener('beforeunload', () => {
    if (pollHandle) clearInterval(pollHandle);
  });
});