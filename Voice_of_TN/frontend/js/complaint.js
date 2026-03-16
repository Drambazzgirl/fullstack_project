// complaint.js - Raise complaint page logic

if (!isLoggedIn()) {
    alert('Please login to raise a complaint');
    window.location.href = './login.html';
} else if (getUserRole() === 'c_admin' || getUserRole() === 'cm_admin') {
    alert('Admins cannot raise complaints!');
    window.location.href = './c_admin_dashboard.html';
}

// ─── Populate Dropdowns ───────────────────────────
function populateDropdowns() {
    const distSel = document.getElementById('district');
    const deptSel = document.getElementById('department');

    DISTRICTS.forEach(d => {
        distSel.innerHTML += `<option value="${d}">${d}</option>`;
    });
    DEPARTMENTS.forEach(d => {
        deptSel.innerHTML += `<option value="${d}">${d}</option>`;
    });
}

function updateSubcategories() {
    const dept   = document.getElementById('department').value;
    const subSel = document.getElementById('subcategory');
    const subs   = SUBCATEGORIES[dept] || [];

    subSel.innerHTML = '<option value="">-- Select Subcategory --</option>';
    subs.forEach(s => {
        subSel.innerHTML += `<option value="${s}">${s}</option>`;
    });
}

// ─── Voice Recording ──────────────────────────────
let mediaRecorder = null;
let audioChunks   = [];
let recordedBlob  = null;
let isRecording   = false;

async function toggleRecording() {
    const btn    = document.getElementById('recordBtn');
    const status = document.getElementById('recordStatus');
    const player = document.getElementById('audioPlayer');

    if (!isRecording) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks   = [];

            mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
            mediaRecorder.onstop = () => {
                recordedBlob         = new Blob(audioChunks, { type: 'audio/webm' });
                player.src           = URL.createObjectURL(recordedBlob);
                player.style.display = 'block';
                stream.getTracks().forEach(t => t.stop());
                document.getElementById('deleteVoiceBtn').style.display = 'inline-block';
            };

            mediaRecorder.start();
            isRecording          = true;
            btn.textContent      = 'Stop Recording';
            btn.style.background = 'var(--danger)';
            btn.style.color      = '#fff';
            btn.style.border     = 'none';
            status.textContent   = 'Recording...';
            status.className     = 'record-status recording';

        } catch (err) {
            status.textContent = 'Microphone access denied';
        }
    } else {
        mediaRecorder.stop();
        isRecording          = false;
        btn.textContent      = '🎙️ Record Again';
        btn.style.background = '';
        btn.style.color      = '';
        btn.style.border     = '';
        status.textContent   = 'Recording saved';
        status.className     = 'record-status';
    }
}

// ─── Delete Voice ─────────────────────────────────
function deleteVoice() {
    recordedBlob = null;
    const player = document.getElementById('audioPlayer');
    const btn    = document.getElementById('recordBtn');
    const status = document.getElementById('recordStatus');
    const delBtn = document.getElementById('deleteVoiceBtn');

    player.src           = '';
    player.style.display = 'none';
    delBtn.style.display = 'none';
    btn.textContent      = '🎙️ Start Recording';
    btn.style.background = '';
    btn.style.color      = '';
    status.textContent   = 'Voice deleted. Record again!';
    status.className     = 'record-status';
}

// ─── Submit Complaint ─────────────────────────────
async function submitComplaint() {
    const citizen_name = document.getElementById('citizen_name').value.trim();
    const age          = document.getElementById('age').value;
    const district     = document.getElementById('district').value;
    const department   = document.getElementById('department').value;
    const subcategory  = document.getElementById('subcategory').value;
    const description  = document.getElementById('description').value.trim();
    const submitBtn    = document.getElementById('submitBtn');
    const successMsg   = document.getElementById('successMsg');
    const errorMsg     = document.getElementById('errorMsg');
    const proofDoc     = document.getElementById('proofDoc').files[0];

    successMsg.style.display = 'none';
    errorMsg.style.display   = 'none';
    document.querySelectorAll('.error-msg').forEach(e => e.style.display = 'none');

    // ─── Validation ───────────────────────────────
    let hasError = false;

    function showErr(id, msg) {
        const el = document.getElementById(id + 'Error');
        if (el) { el.textContent = msg; el.style.display = 'block'; }
        hasError = true;
    }

    if (citizen_name.length < 2) showErr('name', 'Enter your full name');
    if (!age || age < 1 || age > 120) showErr('age', 'Enter a valid age');
    if (!district)    showErr('district', 'Select your district');
    if (!department)  showErr('dept', 'Select a department');
    if (!subcategory) showErr('sub', 'Select a subcategory');
    if (description.length < 20) showErr('desc', 'Describe your issue in at least 20 characters');

    if (hasError) return;

    // ─── Build Form Data ──────────────────────────
    const formData = new FormData();
    formData.append('citizen_name', citizen_name);
    formData.append('age',          age);
    formData.append('district',     district);
    formData.append('department',   department);
    formData.append('subcategory',  subcategory);
    formData.append('description',  description);

    if (recordedBlob) {
        formData.append('voice_file', recordedBlob, 'voice.webm');
    }
    if (proofDoc) {
        formData.append('proof_doc', proofDoc);
    }

    // ─── API Call ─────────────────────────────────
    submitBtn.disabled    = true;
    submitBtn.textContent = 'Submitting...';

    try {
        const res = await fetch(`${API_BASE_URL}/complaints/`, {
            method:  'POST',
            headers: authHeader(),
            body:    formData
        });

        if (res.ok) {
            window.location.href = './profile.html';
        } else {
            const err = await res.json();
            errorMsg.textContent   = err.detail || 'Submission failed';
            errorMsg.style.display = 'block';
        }
    } catch (err) {
        errorMsg.textContent   = 'Network error. Please try again.';
        errorMsg.style.display = 'block';
    } finally {
        submitBtn.disabled    = false;
        submitBtn.textContent = 'Submit Complaint';
    }
}

// ─── Init ─────────────────────────────────────────
populateDropdowns();

const savedName = getUserName();
if (savedName) document.getElementById('citizen_name').value = savedName;