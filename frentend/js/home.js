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

// Render a complaint card
function renderComplaintCard(c) {
  const card = el('div', { class: 'complaint-card' });

  if (c.image_url) {
    const thumb = el('img', { src: c.image_url, class: 'complaint-thumb', alt: c.title });
    card.appendChild(thumb);
  }

  const body = el('div', { class: 'complaint-body' });
  body.appendChild(el('h3', { text: c.title }));

  const meta = el('div', { class: 'complaint-meta' });
  meta.appendChild(el('span', { class: 'complaint-department', text: c.department }));
  meta.appendChild(el('span', { class: 'complaint-status', text: String(c.status) }));
  meta.appendChild(el('span', { class: 'complaint-created', text: new Date(c.created_at).toLocaleString() }));
  body.appendChild(meta);

  const snippet = el('p', { class: 'complaint-snippet', text: c.description.length > 150 ? c.description.slice(0, 147) + '...' : c.description });
  body.appendChild(snippet);

  const actions = el('div', { class: 'complaint-actions' });
  const view = el('a', { href: `complaint_details.html?id=${c.id}`, class: 'btn btn-view', text: 'View' });
  actions.appendChild(view);
  body.appendChild(actions);

  card.appendChild(body);
  return card;
}

async function loadComplaints() {
  const dept = document.getElementById('filter-department').value;
  const status = document.getElementById('filter-status').value;
  const params = {};
  if (dept !== 'all') params.department = dept;
  if (status !== 'all') params.status = status;

  try {
    const list = await api.getComplaints(params);
    renderList(list);
  } catch (err) {
    console.error('Error fetching complaints', err);
    showError(err.body?.detail || err.message || 'Failed to fetch');
  }
}

function renderList(list) {
  const container = document.getElementById('complaints-list');
  container.innerHTML = '';

  const depts = new Set();
  list.forEach(c => {
    depts.add(c.department);
    container.appendChild(renderComplaintCard(c));
  });

  populateDepartmentFilter(Array.from(depts).sort());
}

function populateDepartmentFilter(depts) {
  const sel = document.getElementById('filter-department');
  const current = sel.value;
  sel.innerHTML = '';
  sel.appendChild(new Option('All Departments', 'all'));
  depts.forEach(d => sel.appendChild(new Option(d, d)));
  if ([...sel.options].some(o => o.value === current)) sel.value = current;
}

function showError(msg) {
  const elErr = document.getElementById('error-msg');
  if (!elErr) return;
  elErr.textContent = msg;
  elErr.style.display = 'block';
  setTimeout(() => (elErr.style.display = 'none'), 5000);
}

// Wire up filters and auto-refresh
document.addEventListener('DOMContentLoaded', async () => {
  document.getElementById('filter-department').addEventListener('change', loadComplaints);
  document.getElementById('filter-status').addEventListener('change', loadComplaints);

  await loadComplaints();

  // Poll to auto-refresh list so status changes appear in UI
  setInterval(loadComplaints, 15000);
});