// login.js - Login page logic

// Redirect if already logged in
if (isLoggedIn()) window.location.href = './index.html';

// Hide Toggle Function
function togglePassword(id) {
    const input = document.getElementById(id);
    input.type = input.type === 'password' ? 'text' : 'password';
}

async function handleLogin() {
    const email     = document.getElementById('email').value.trim();
    const password  = document.getElementById('password').value;
    const submitBtn = document.getElementById('submitBtn');
    const errorDiv  = document.getElementById('loginError');

    errorDiv.style.display = 'none';

    if (!email || !password) {
        errorDiv.textContent   = 'Please enter email and password';
        errorDiv.style.display = 'block';
        return;
    }

    submitBtn.disabled    = true;
    submitBtn.textContent = 'Logging in...';

    try {
        const res = await fetch(`${API_BASE_URL}/auth/login/json`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ username: email, password })
        });

        if (!res.ok) {
            const err = await res.json();
            errorDiv.textContent   = err.detail || 'Invalid email or password';
            errorDiv.style.display = 'block';
            return;
        }

        const data = await res.json();
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('token_type',   data.token_type);
        localStorage.setItem('user_email',   data.email);
        localStorage.setItem('role',         data.role);
        localStorage.setItem('user_name',    data.name);

        window.location.href = './index.html';

    } catch (err) {
        errorDiv.textContent   = 'Something went wrong. Please try again.';
        errorDiv.style.display = 'block';
    } finally {
        submitBtn.disabled    = false;
        submitBtn.textContent = 'Login';
    }
}

document.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') handleLogin();
});

