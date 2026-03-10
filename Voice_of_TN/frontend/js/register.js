// register.js - Registration page logic

// Redirect if already logged in
if (isLoggedIn()) window.location.href = './index.html';

function showError(id, msg) {
    const el = document.getElementById(id + 'Error');
    el.textContent = msg;
    el.style.display = 'block';
}

function clearErrors() {
    document.querySelectorAll('.error-msg').forEach(el => {
        el.style.display = 'none';
        el.textContent   = '';
    });
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function isValidPhone(phone) {
    return /^[6-9][0-9]{9}$/.test(phone);
}

async function handleRegister() {
    clearErrors();

    const name            = document.getElementById('name').value.trim();
    const email           = document.getElementById('email').value.trim();
    const phone           = document.getElementById('phone').value.trim();
    const password        = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const submitBtn       = document.getElementById('submitBtn');
    const successMsg      = document.getElementById('successMsg');

    // ─── Validation ───────────────────────────────
    let hasError = false;

    if (name.length < 2) {
        showError('name', 'Name must be at least 2 characters');
        hasError = true;
    }
    if (!isValidEmail(email)) {
        showError('email', 'Please enter a valid email address');
        hasError = true;
    }
    if (!isValidPhone(phone)) {
        showError('phone', 'Enter a valid 10-digit Indian mobile number');
        hasError = true;
    }
    if (password.length < 6) {
        showError('password', 'Password must be at least 6 characters');
        hasError = true;
    }
    if (password !== confirmPassword) {
        showError('confirm', 'Passwords do not match');
        hasError = true;
    }

    if (hasError) return;

    // ─── Register API Call ────────────────────────
    submitBtn.disabled    = true;
    submitBtn.textContent = 'Creating account...';

    try {
        const regRes = await fetch(`${API_BASE_URL}/auth/register`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ name, email, phone, password })
        });

        if (!regRes.ok) {
            const err = await regRes.json();
            showError('email', err.detail || 'Registration failed');
            return;
        }

        // ─── Auto Login after Register ────────────
        const loginRes = await fetch(`${API_BASE_URL}/auth/login/json`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ username: email, password })
        });

        if (!loginRes.ok) {
            // Registration done but login failed — go to login page
            successMsg.textContent    = 'Registered! Please login.';
            successMsg.style.display  = 'block';
            setTimeout(() => window.location.href = './login.html', 1500);
            return;
        }

        const loginData = await loginRes.json();

        // Save to localStorage
        localStorage.setItem('access_token', loginData.access_token);
        localStorage.setItem('token_type',   loginData.token_type);
        localStorage.setItem('user_email',   loginData.email);
        localStorage.setItem('role',         loginData.role);
        localStorage.setItem('user_name',    loginData.name);

        // Show success and redirect
        successMsg.textContent   = 'Account created! Redirecting to home...';
        successMsg.style.display = 'block';
        setTimeout(() => window.location.href = './index.html', 1000);

    } catch (error) {
        showError('email', 'Something went wrong. Please try again.');
        console.error(error);
    } finally {
        submitBtn.disabled    = false;
        submitBtn.textContent = 'Create Account';
    }
}

// Allow pressing Enter to submit
document.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') handleRegister();
});

// Hide Toggle Function
function togglePassword(id) {
    const input = document.getElementById(id);
    input.type = input.type === 'password' ? 'text' : 'password';
}