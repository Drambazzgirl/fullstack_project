// admin_login.js - Admin login page

async function handleAdminLogin() {
    const role      = document.getElementById('adminRole').value;
    const username  = document.getElementById('username').value.trim();
    const password  = document.getElementById('password').value;
    const submitBtn = document.getElementById('submitBtn');
    const errorDiv  = document.getElementById('loginError');

    errorDiv.style.display = 'none';

    if (!username || !password) {
        errorDiv.textContent   = 'Please enter username and password';
        errorDiv.style.display = 'block';
        return;
    }

    submitBtn.disabled    = true;
    submitBtn.textContent = 'Logging in...';

    try {
        const res = await fetch(`${API_BASE_URL}/admin/login`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ username, password, role })
        });

        if (!res.ok) {
            const err = await res.json();
            errorDiv.textContent   = err.detail || 'Invalid credentials';
            errorDiv.style.display = 'block';
            return;
        }

        const data = await res.json();
        localStorage.setItem('access_token',  data.access_token);
        localStorage.setItem('token_type',    data.token_type);
        localStorage.setItem('role',          data.role);
        localStorage.setItem('admin_username',data.username);
        localStorage.setItem('user_name',     data.name);

        // Redirect based on role
        if (data.role === 'c_admin') {
            window.location.href = './c_admin_dashboard.html';
        } else {
            window.location.href = './cm_admin_dashboard.html';
        }

    } catch (err) {
        errorDiv.textContent   = 'Something went wrong. Please try again.';
        errorDiv.style.display = 'block';
    } finally {
        submitBtn.disabled    = false;
        submitBtn.textContent = 'Login as Admin';
    }
}

document.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') handleAdminLogin();
});
