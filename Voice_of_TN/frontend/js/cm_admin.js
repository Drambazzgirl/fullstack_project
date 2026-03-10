// cm_admin.js - CM Admin Dashboard

if (!isLoggedIn() || getUserRole() !== 'cm_admin') {
    alert('Access denied. Please login as CM Admin.');
    window.location.href = './admin_login.html';
}

document.getElementById('adminName').textContent = localStorage.getItem('user_name') || 'CM Admin';

function adminLogout() {
    localStorage.clear();
    window.location.href = './admin_login.html';
}

let allComplaints = [];
let selectedId    = null;

const DEPT_ICONS = {
    "Agriculture Department":              "🌾",
    "Finance Department":                  "💰",
    "Health and Family Welfare Department":"🏥",
    "School Education Department":         "📚",
    "Public Works Department":             "🏗️",
    "Animal Husbandry, Dairying and Fisheries Department": "🐄"
};

function buildFilters() {
    DEPARTMENTS.forEach(d => {
        document.getElementById('aDept').innerHTML += `<option value="${d}">${d}</option>`;
    });
}

async function loadComplaints() {
    try {
        const res     = await fetch(`${API_BASE_URL}/complaints/`);
        allComplaints = await res.json();
        buildStats(allComplaints);
        applyFilter();
    } catch (err) {
        document.getElementById('adminList').innerHTML = '<p style="color:var(--danger)">Failed to load</p>';
    }
}

function buildStats(data) {
    const counts = { total: data.length, pending: 0, under_investigation: 0, resolved: 0, rejected: 0, solved: 0 };
    data.forEach(c => { if (counts[c.status] !== undefined) counts[c.status]++; });

    document.getElementById('adminStats').innerHTML = `
        <div class="astat"><span class="anum">${counts.total}</span><div class="alabel">Total</div></div>
        <div class="astat warning"><span class="anum">${counts.pending}</span><div class="alabel">Pending</div></div>
        <div class="astat info"><span class="anum">${counts.under_investigation}</span><div class="alabel">Investigating</div></div>
        <div class="astat success"><span class="anum">${counts.resolved}</span><div class="alabel">Resolved</div></div>
        <div class="astat danger"><span class="anum">${counts.rejected}</span><div class="alabel">Rejected</div></div>
        <div class="astat solved"><span class="anum">${counts.solved}</span><div class="alabel">Solved</div></div>
    `;
}

function applyFilter() {
    const dept   = document.getElementById('aDept').value;
    const status = document.getElementById('aStatus').value;
    let filtered = allComplaints;
    if (dept)   filtered = filtered.filter(c => c.department === dept);
    if (status) filtered = filtered.filter(c => c.status     === status);
    renderList(filtered);
}

function renderList(data) {
    const list = document.getElementById('adminList');
    if (data.length === 0) {
        list.innerHTML = '<div class="empty-state"><div class="icon">📭</div><p>No complaints found</p></div>';
        return;
    }
    list.innerHTML = '';
    data.forEach((c, i) => {
        const item = document.createElement('div');
        item.className = `admin-complaint-item status-${c.status}`;
        item.style.animationDelay = `${Math.min(i, 15) * 0.05}s`;
        item.innerHTML = `
            <div class="aci-header">
                <div class="aci-left">
                    <span class="aci-dept">${DEPT_ICONS[c.department] || '📋'} ${c.department.replace(' Department','')}</span>
                    <span class="aci-name">${c.citizen_name} (Age: ${c.age})</span>
                    <span class="aci-meta">📍 ${c.district} &nbsp;|&nbsp; #${c.id} &nbsp;|&nbsp; ${c.subcategory}</span>
                </div>
                <div class="aci-right">
                    ${statusBadge(c.status)}
                    ${c.status === 'pending' || c.status === 'resolved' ? `
                        <button class="btn btn-primary" style="padding:7px 14px;font-size:0.82rem"
                            onclick="openModal(${c.id}, '${c.subcategory.replace(/'/g, "\\'")}')">
                            Update
                        </button>` : ''}
                </div>
            </div>
            <div class="aci-desc">${c.description}</div>
            <div class="aci-footer">
                <div class="aci-info">
                    <span>📅 ${formatDate(c.created_at)}</span>
                    ${c.voice_file ? `
                        <a href="http://localhost:8000${c.voice_file}" target="_blank"
                            style="color:#fff;font-size:0.82rem;background:rgba(255,255,255,0.2);
                            padding:4px 10px;border-radius:6px;text-decoration:none">
                            🎙️ Play Voice
                        </a>` : ''}
                    ${c.proof_doc ? `
                        <a href="http://localhost:8000${c.proof_doc}" target="_blank"
                            style="color:#fff;font-size:0.82rem;background:rgba(255,255,255,0.2);
                            padding:4px 10px;border-radius:6px;text-decoration:none">
                            📄 View Proof
                        </a>` : ''}
                </div>
            </div>
            ${c.admin_message ? `<div class="aci-admin-msg">💬 Admin message: ${c.admin_message}</div>` : ''}
        `;
        list.appendChild(item);
    });
}

function openModal(id, desc) {
    selectedId = id;
    document.getElementById('modalId').textContent   = `#${id}`;
    document.getElementById('modalDesc').textContent = desc;
    document.getElementById('adminMsg').value        = '';
    document.getElementById('modal').style.display   = 'flex';
}

function closeModal() {
    document.getElementById('modal').style.display = 'none';
    selectedId = null;
}

async function updateStatus() {
    const status  = document.getElementById('newStatus').value;
    const message = document.getElementById('adminMsg').value.trim();

    if (status === 'solved' && !message) {
        alert('Please add a message to the citizen when marking as Solved');
        return;
    }

    try {
        const res = await fetch(`${API_BASE_URL}/complaints/${selectedId}/status`, {
            method:  'PUT',
            headers: { ...authHeader(), 'Content-Type': 'application/json' },
            body:    JSON.stringify({ status, message: message || null })
        });

        if (res.ok) {
            closeModal();
            loadComplaints();
        } else {
            const err = await res.json();
            alert(err.detail || 'Update failed');
        }
    } catch (err) {
        alert('Network error');
    }
}

document.getElementById('modal').addEventListener('click', function(e) {
    if (e.target === this) closeModal();
});

buildFilters();
loadComplaints();