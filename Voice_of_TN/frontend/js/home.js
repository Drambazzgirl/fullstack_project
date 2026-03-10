// home.js - Home page logic

// ─── Update Navbar based on login state ───────────
function updateNav() {
    const loggedIn = isLoggedIn();
    document.getElementById('navDashboard').style.display = loggedIn ? 'block' : 'none';
    document.getElementById('navRaise').style.display     = loggedIn ? 'inline-flex' : 'none';
    document.getElementById('navLogin').style.display     = loggedIn ? 'none' : 'block';
    document.getElementById('navRegister').style.display  = loggedIn ? 'none' : 'block';
    document.getElementById('navLogout').style.display    = loggedIn ? 'block' : 'none';
}

// ─── Department Icons Map ─────────────────────────
const DEPT_ICONS = {
    "Agriculture Department":              "🌾",
    "Finance Department":                  "💰",
    "Health and Family Welfare Department":"🏥",
    "School Education Department":         "📚",
    "Public Works Department":             "🏗️",
    "Animal Husbandry, Dairying and Fisheries Department": "🐄"
};

// ─── Build Department Cards ───────────────────────
function buildDeptCards(complaints) {
    const grid = document.getElementById('deptGrid');
    grid.innerHTML = '';

    DEPARTMENTS.forEach(dept => {
        const count = complaints.filter(c => c.department === dept).length;
        const card  = document.createElement('a');
        card.className = 'dept-card';
        card.href = `./complaints_view.html?dept=${encodeURIComponent(dept)}`;
        card.innerHTML = `
            <span class="dept-icon">${DEPT_ICONS[dept] || '📋'}</span>
            <span class="dept-name">${dept}</span>
            <span class="dept-count">${count} complaint${count !== 1 ? 's' : ''}</span>
        `;
        grid.appendChild(card);
    });
}

// ─── Populate Filter Dropdowns ────────────────────
function buildFilters() {
    const deptSel = document.getElementById('filterDept');
    const distSel = document.getElementById('filterDistrict');

    DEPARTMENTS.forEach(d => {
        deptSel.innerHTML += `<option value="${d}">${d}</option>`;
    });
    DISTRICTS.forEach(d => {
        distSel.innerHTML += `<option value="${d}">${d}</option>`;
    });
}

// ─── Load and Display Complaints ──────────────────
let allComplaints = [];

async function loadComplaints() {
    try {
        const res  = await fetch(`${API_BASE_URL}/complaints/`);
        allComplaints = await res.json();
        updateStats(allComplaints);
        buildDeptCards(allComplaints);
        renderComplaints(allComplaints);
    } catch (err) {
        document.getElementById('complaintsContainer').innerHTML =
            '<p style="color:var(--danger);text-align:center">Failed to load complaints</p>';
    }
}

function updateStats(data) {
    document.getElementById('totalCount').textContent   = data.length;
    document.getElementById('pendingCount').textContent = data.filter(c => c.status === 'pending').length;
    document.getElementById('solvedCount').textContent  = data.filter(c => c.status === 'solved').length;
}

function renderComplaints(data) {
    const container = document.getElementById('complaintsContainer');
    if (data.length === 0) {
        container.innerHTML = `<div class="empty-state"><div class="icon">📭</div><p>No complaints found</p></div>`;
        return;
    }

    const grid = document.createElement('div');
    grid.className = 'complaints-grid';

    data.forEach((c, i) => {
        const card = document.createElement('div');
        card.className = `complaint-card status-${c.status}`;
        card.style.animationDelay = `${i * 0.05}s`;
        card.innerHTML = `
            <div class="card-top">
                <span class="dept-tag">${DEPT_ICONS[c.department] || ''} ${c.department.replace(' Department','')}</span>
                <span class="complaint-id">#${c.id}</span>
            </div>
            <h4>${c.citizen_name} — ${c.subcategory}</h4>
            <p>${c.description}</p>
            <div class="card-footer">
                <span>${c.district}</span>
                ${statusBadge(c.status)}
                <span>${formatDate(c.created_at)}</span>
            </div>
            ${c.admin_message ? `<div style="margin-top:10px;padding:8px 12px;background:rgba(142,68,173,0.08);border-radius:6px;font-size:0.82rem;color:#6C3483">💬 <b>Admin:</b> ${c.admin_message}</div>` : ''}
        `;
        grid.appendChild(card);
    });

    container.innerHTML = '';
    container.appendChild(grid);
}

// ─── Filter Complaints ────────────────────────────
function filterComplaints() {
    const dept     = document.getElementById('filterDept').value;
    const status   = document.getElementById('filterStatus').value;
    const district = document.getElementById('filterDistrict').value;

    let filtered = allComplaints;
    if (dept)     filtered = filtered.filter(c => c.department === dept);
    if (status)   filtered = filtered.filter(c => c.status === status);
    if (district) filtered = filtered.filter(c => c.district === district);

    renderComplaints(filtered);
}

// ─── Init ─────────────────────────────────────────
updateNav();
buildFilters();
loadComplaints();
