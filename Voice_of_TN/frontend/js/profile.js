// profile.js - Profile page logic

if (!isLoggedIn()) {
    alert('Please login to view your profile');
    window.location.href = './login.html';
}

const API     = API_BASE_URL;
const BACKEND = 'http://localhost:8000';

// ─── Load User Profile ────────────────────────────
async function loadProfile() {
    try {
        const res  = await fetch(`${API}/auth/me`, { headers: authHeader() });
        const user = await res.json();

        document.getElementById('profileName').textContent  = user.name;
        document.getElementById('profileEmail').textContent = user.email || '';

        if (user.profile_picture) {
            document.getElementById('profileImg').src = BACKEND + user.profile_picture;
        }

        document.getElementById('editName').value     = user.name     || '';
        document.getElementById('editPhone').value    = user.phone    || '';
        document.getElementById('editAge').value      = user.age      || '';
        document.getElementById('editDistrict').value = user.district || '';

    } catch (err) {
        console.error('Profile load failed', err);
    }
}

// ─── Populate District Dropdown ───────────────────
function populateDistrict() {
    const sel = document.getElementById('editDistrict');
    DISTRICTS.forEach(d => {
        sel.innerHTML += `<option value="${d}">${d}</option>`;
    });
}

// ─── Save Profile ─────────────────────────────────
async function saveProfile() {
    const name      = document.getElementById('editName').value.trim();
    const phone     = document.getElementById('editPhone').value.trim();
    const age       = parseInt(document.getElementById('editAge').value) || null;
    const district  = document.getElementById('editDistrict').value;
    const successEl = document.getElementById('editSuccess');

    try {
        const res = await fetch(`${API}/auth/me`, {
            method:  'PUT',
            headers: { ...authHeader(), 'Content-Type': 'application/json' },
            body:    JSON.stringify({ name, phone, age, district })
        });

        if (res.ok) {
            const updated = await res.json();
            document.getElementById('profileName').textContent = updated.name;
            localStorage.setItem('user_name', updated.name);
            successEl.textContent    = 'Profile updated successfully!';
            successEl.style.display  = 'block';
            setTimeout(() => successEl.style.display = 'none', 3000);
        }
    } catch (err) {
        console.error('Update failed', err);
    }
}

// ─── Upload Profile Picture ───────────────────────
async function uploadPic(input) {
    if (!input.files[0]) return;

    const formData = new FormData();
    formData.append('file', input.files[0]);

    try {
        const res  = await fetch(`${API}/auth/upload-profile-picture`, {
            method:  'POST',
            headers: authHeader(),
            body:    formData
        });
        const data = await res.json();
        if (data.profile_picture) {
            document.getElementById('profileImg').src = BACKEND + data.profile_picture;
        }
    } catch (err) {
        console.error('Upload failed', err);
    }
}

// ─── Load My Complaints ───────────────────────────
async function loadMyComplaints() {
    const container = document.getElementById('myComplaints');
    const statsDiv  = document.getElementById('myStats');

    try {
        const res        = await fetch(`${API}/complaints/my`, { headers: authHeader() });
        const complaints = await res.json();

        const counts = { pending: 0, under_investigation: 0, resolved: 0, rejected: 0, solved: 0 };
        complaints.forEach(c => { if (counts[c.status] !== undefined) counts[c.status]++; });

        statsDiv.innerHTML = `
            <div class="cstat"><span class="cnum" style="color:var(--warning)">${counts.pending}</span><div class="clabel">Pending</div></div>
            <div class="cstat"><span class="cnum" style="color:var(--info)">${counts.under_investigation}</span><div class="clabel">Investigating</div></div>
            <div class="cstat"><span class="cnum" style="color:var(--success)">${counts.resolved}</span><div class="clabel">Resolved</div></div>
            <div class="cstat"><span class="cnum" style="color:var(--danger)">${counts.rejected}</span><div class="clabel">Rejected</div></div>
            <div class="cstat"><span class="cnum" style="color:var(--solved)">${counts.solved}</span><div class="clabel">Solved</div></div>
        `;

        if (complaints.length === 0) {
            container.innerHTML = `<div class="empty-state"><div class="icon">📭</div><p>No complaints yet. <a href="./complaint.html">Raise one now</a></p></div>`;
            return;
        }

        container.innerHTML = '';
        complaints.forEach((c, i) => {
            const item = document.createElement('div');
            item.className         = `my-complaint-item status-${c.status}`;
            item.style.animationDelay = `${i * 0.07}s`;
            item.innerHTML = `
                <div class="mci-top">
                    <span class="mci-dept">${c.department.replace(' Department', '')}</span>
                    <div style="display:flex;align-items:center;gap:8px">
                        ${statusBadge(c.status)}
                        <span class="mci-date">#${c.id}</span>
                    </div>
                </div>
                <b style="font-size:0.92rem">${c.subcategory}</b>
                <p class="mci-desc">${c.description}</p>
                <div class="mci-bottom">
                    <span style="font-size:0.78rem;color:var(--text-light)">${c.district}</span>
                    <span style="font-size:0.78rem;color:var(--text-light)">${formatDate(c.created_at)}</span>
                    ${c.voice_file ? `<a href="${BACKEND}${c.voice_file}" target="_blank" style="font-size:0.78rem;color:var(--primary)">🎙️ Voice</a>` : ''}
                    ${c.proof_doc  ? `<a href="${BACKEND}${c.proof_doc}"  target="_blank" style="font-size:0.78rem;color:var(--primary)">📄 Proof</a>`  : ''}
                    ${c.status === 'pending' ? `
                        <button onclick="openEdit(${c.id}, \`${c.description.replace(/`/g, '')}\`, '${c.subcategory}')"
                            style="font-size:0.78rem;padding:4px 10px;background:var(--info);color:#fff;border:none;border-radius:6px;cursor:pointer">
                            ✏️ Edit
                        </button>
                        <button onclick="deleteComplaint(${c.id})"
                            style="font-size:0.78rem;padding:4px 10px;background:var(--danger);color:#fff;border:none;border-radius:6px;cursor:pointer">
                            🗑️ Delete
                        </button>
                    ` : ''}
                </div>
                ${c.admin_message ? `<div class="mci-admin-msg">💬 ${c.admin_message}</div>` : ''}
            `;
            container.appendChild(item);
        });

    } catch (err) {
        container.innerHTML = '<p style="color:var(--danger)">Failed to load complaints</p>';
    }
}

// ─── Delete Complaint ─────────────────────────────
async function deleteComplaint(id) {
    if (!confirm('Are you sure you want to delete this complaint?')) return;

    try {
        const res = await fetch(`${API}/complaints/${id}`, {
            method:  'DELETE',
            headers: authHeader()
        });
        if (res.ok) {
            loadMyComplaints();
        } else {
            alert('Delete failed');
        }
    } catch (err) {
        alert('Network error');
    }
}

// ─── Edit Complaint ───────────────────────────────
function openEdit(id, description, subcategory) {
    document.getElementById('editComplaintId').value  = id;
    document.getElementById('editDescription').value  = description;
    document.getElementById('editSubcategory').value  = subcategory;
    document.getElementById('editModal').style.display = 'flex';
}

function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
}

async function saveEdit() {
    const id          = document.getElementById('editComplaintId').value;
    const description = document.getElementById('editDescription').value.trim();
    const subcategory = document.getElementById('editSubcategory').value.trim();

    if (!description) { alert('Description எழுதுங்க'); return; }

    try {
        const res = await fetch(`${API}/complaints/${id}/edit`, {
            method:  'PUT',
            headers: { ...authHeader(), 'Content-Type': 'application/json' },
            body:    JSON.stringify({ description, subcategory })
        });
        if (res.ok) {
            closeEditModal();
            loadMyComplaints();
        } else {
            alert('Update failed');
        }
    } catch (err) {
        alert('Network error');
    }
}

// ─── Init ─────────────────────────────────────────
populateDistrict();
loadProfile();
loadMyComplaints();