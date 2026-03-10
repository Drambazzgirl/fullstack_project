// complaints_view.js - All complaints page

// Update navbar
function updateNav() {
    const loggedIn = isLoggedIn();
    const role = getUserRole();
    
    // Admin na avenga dashbored kke poganum.
    if (role === 'c_admin') {
        document.getElementById('navDashboard').href = './c_admin_dashboard.html';
    } else if (role === 'cm_admin') {
        document.getElementById('navDashboard').href = './cm_admin_dashboard.html';
    }

    document.getElementById('navDashboard').style.display = loggedIn ? 'block' : 'none';
    document.getElementById('navRaise').style.display     = (loggedIn && role === 'citizen') ? 'inline-flex' : 'none';
    document.getElementById('navLogin').style.display     = loggedIn ? 'none' : 'block';
    document.getElementById('navRegister').style.display  = loggedIn ? 'none' : 'block';
    document.getElementById('navLogout').style.display    = loggedIn ? 'block' : 'none';
}

// Populate filter dropdowns
function buildFilters() {
    DEPARTMENTS.forEach(d => {
        document.getElementById('fDept').innerHTML += `<option value="${d}">${d}</option>`;
    });
    DISTRICTS.forEach(d => {
        document.getElementById('fDistrict').innerHTML += `<option value="${d}">${d}</option>`;
    });

    // Check if dept filter from URL
    const params = new URLSearchParams(window.location.search);
    const dept   = params.get('dept');
    if (dept) document.getElementById('fDept').value = dept;
}

let allComplaints = [];

async function loadComplaints() {
    try {
        const res   = await fetch(`${API_BASE_URL}/complaints/`);
        allComplaints = await res.json();
        applyFilters();
    } catch (err) {
        document.getElementById('cvList').innerHTML =
            '<p style="color:var(--danger);text-align:center">Failed to load complaints</p>';
    }
}

function applyFilters() {
    const dept     = document.getElementById('fDept').value;
    const status   = document.getElementById('fStatus').value;
    const district = document.getElementById('fDistrict').value;

    let filtered = allComplaints;
    if (dept)     filtered = filtered.filter(c => c.department === dept);
    if (status)   filtered = filtered.filter(c => c.status     === status);
    if (district) filtered = filtered.filter(c => c.district   === district);

    renderComplaints(filtered);
}

function clearFilters() {
    document.getElementById('fDept').value     = '';
    document.getElementById('fStatus').value   = '';
    document.getElementById('fDistrict').value = '';
    applyFilters();
}

const DEPT_ICONS = {
    "Agriculture Department":              "🌾",
    "Finance Department":                  "💰",
    "Health and Family Welfare Department":"🏥",
    "School Education Department":         "📚",
    "Public Works Department":             "🏗️",
    "Animal Husbandry, Dairying and Fisheries Department": "🐄"
};

function renderComplaints(data) {
    const list  = document.getElementById('cvList');
    const count = document.getElementById('cvCount');

    count.textContent = `Showing ${data.length} complaint${data.length !== 1 ? 's' : ''}`;

    if (data.length === 0) {
        list.innerHTML = `<div class="empty-state"><div class="icon"></div><p>No complaints found</p></div>`;
        return;
    }

    const grid = document.createElement('div');
    grid.className = 'cv-grid';

    data.forEach((c, i) => {
        const card = document.createElement('div');
        card.className = `cv-card status-${c.status}`;
        card.style.animationDelay = `${Math.min(i, 20) * 0.04}s`;
        card.innerHTML = `
            <div class="cv-card-top">
                <span class="cv-dept-tag">${DEPT_ICONS[c.department] || ''} ${c.department.replace(' Department','')}</span>
                <span class="cv-id">#${c.id}</span>
            </div>
            <div class="cv-sub">${c.citizen_name} — ${c.subcategory}</div>
            <div class="cv-desc">${c.description}</div>
            <div class="cv-footer">
                <span>${c.district}</span>
                ${statusBadge(c.status)}
                <span>${formatDate(c.created_at)}</span>
            </div>
            ${c.admin_message ? `<div class="cv-admin-msg"><b>Admin:</b> ${c.admin_message}</div>` : ''}
        `;
        grid.appendChild(card);
    });

    list.innerHTML = '';
    list.appendChild(grid);
}

// Init
updateNav();
buildFilters();
loadComplaints();
