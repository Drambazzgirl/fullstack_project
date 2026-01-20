// const API_URL = "http://localhost:8000";

// // --- Auth Utilities ---

// function getToken() {
//     return localStorage.getItem('access_token');
// }

// function setToken(token) {
//     localStorage.setItem('access_token', token);
// }

// function removeToken() {
//     localStorage.removeItem('access_token');
// }

// function logout() {
//     removeToken();
//     window.location.href = 'login.html';
// }

// function adminLogout() {
//     removeToken();
//     window.location.href = 'admin_login.html'; // Adjust filename if needed
// }

// function checkAuth() {
//     const token = getToken();
//     const path = window.location.pathname;
//     if (!token && !path.includes('login.html') && !path.includes('register.html') && !path.includes('index.html') && !path.includes('complaints_view.html')) {
//         // Redirect to login if trying to access protected pages
//         // window.location.href = 'login.html';
//     }
// }

// async function apiRequest(endpoint, method = 'GET', body = null, isForm = false) {
//     const headers = {};
//     const token = getToken();
//     if (token) {
//         headers['Authorization'] = `Bearer ${token}`;
//     }

//     const options = {
//         method,
//         headers,
//     };

//     if (body) {
//         if (isForm) {
//             // Do not set Content-Type, browser sets it for FormData
//             options.body = body;
//         } else {
//             headers['Content-Type'] = 'application/json';
//             options.body = JSON.stringify(body);
//         }
//     }

//     try {
//         const response = await fetch(`${API_URL}${endpoint}`, options);
//         if (response.status === 401) {
//             logout(); // Token expired
//             return null;
//         }
//         return response;
//     } catch (error) {
//         console.error("API Error:", error);
//         alert("Server error. Is the backend running?");
//         return null;
//     }
// }

// // --- Page Specific Logic ---

// document.addEventListener('DOMContentLoaded', () => {
//     checkAuth();

//     // Login
//     const loginForm = document.getElementById('loginForm');
//     if (loginForm) {
//         loginForm.addEventListener('submit', async (e) => {
//             e.preventDefault();
//             const email = document.getElementById('email').value;
//             const password = document.getElementById('password').value;

//             // FormData for OAuth2 standard
//             const formData = new FormData();
//             formData.append('username', email);
//             formData.append('password', password);

//             const res = await fetch(`${API_URL}/auth/login`, {
//                 method: 'POST',
//                 body: formData
//             });

//             if (res.ok) {
//                 const data = await res.json();
//                 setToken(data.access_token);
//                 // Optionally get user role to decide redirect
//                 window.location.href = 'profile.html';
//             } else {
//                 alert('Login failed');
//             }
//         });
//     }

//     // Register
//     const registerForm = document.getElementById('registerForm');
//     if (registerForm) {
//         registerForm.addEventListener('submit', async (e) => {
//             e.preventDefault();
//             const name = document.getElementById('name').value;
//             const email = document.getElementById('email').value;
//             const phone = document.getElementById('phone').value;
//             const password = document.getElementById('password').value;
//             const confirm = document.getElementById('confirmPassword').value;

//             if (password !== confirm) {
//                 alert("Passwords do not match");
//                 return;
//             }

//             const res = await apiRequest('/auth/register', 'POST', {
//                 name, email, phone, password
//             });

//             if (res && res.ok) {
//                 alert('Registration successful! Please login.');
//                 window.location.href = 'login.html';
//             } else {
//                 const data = await res.json();
//                 alert(data.detail || 'Registration failed');
//             }
//         });
//     }

//     // Admin Login
//     const adminLoginForm = document.getElementById('adminLoginForm');
//     if (adminLoginForm) {
//         adminLoginForm.addEventListener('submit', async (e) => {
//             e.preventDefault();
//             const email = document.getElementById('email').value;
//             const password = document.getElementById('password').value;

//             const formData = new FormData();
//             formData.append('username', email);
//             formData.append('password', password);

//             const res = await fetch(`${API_URL}/auth/admin-login`, {
//                 method: 'POST',
//                 body: formData
//             });

//             if (res.ok) {
//                 const data = await res.json();
//                 setToken(data.access_token);
//                 window.location.href = 'admin_dashboard.html';
//             } else {
//                 alert('Admin login failed');
//             }
//         });
//     }

//     // Profile
//     if (window.location.pathname.includes('profile.html')) {
//         loadProfile();
//         loadMyComplaints();

//         const profileForm = document.getElementById('profileForm');
//         if (profileForm) {
//             profileForm.addEventListener('submit', async (e) => {
//                 e.preventDefault();
//                 await updateProfile();
//             });
//         }
//     }

//     // Departments Load
//     if (document.getElementById('departmentGrid')) {
//         loadDepartments();
//     }

//     // Complaint Submit
//     const complaintForm = document.getElementById('complaintForm');
//     if (complaintForm) {
//         // Pre-fill dept
//         const urlParams = new URLSearchParams(window.location.search);
//         const dept = urlParams.get('dept');
//         if (dept) {
//             document.getElementById('deptName').textContent = dept;
//         }

//         complaintForm.addEventListener('submit', async (e) => {
//             e.preventDefault();
//             const formData = new FormData();
//             formData.append('title', document.getElementById('title').value);
//             formData.append('description', document.getElementById('description').value);
//             formData.append('subcategory', document.getElementById('subcategory').value);
//             formData.append('incident_address', document.getElementById('address').value);
//             formData.append('incident_age', document.getElementById('age').value);
//             formData.append('incident_gender', document.getElementById('gender').value);
//             formData.append('department_name', document.getElementById('deptName').textContent || "General");

//             const fileInput = document.getElementById('file');
//             if (fileInput.files[0]) {
//                 formData.append('file', fileInput.files[0]);
//             }

//             const res = await apiRequest('/complaints/', 'POST', formData, true); // true for form/multipart
//             if (res && res.ok) {
//                 alert('Complaint submitted!');
//                 window.location.href = 'profile.html';
//             } else {
//                 alert('Submission failed');
//             }
//         });
//     }

//     // Admin Dashboard
//     if (window.location.pathname.includes('admin_dashboard.html') || document.getElementById('stats-grid') || document.getElementById('totalComplaints')) {
//         loadAdminStats();
//         loadAllComplaintsAdmin();
//     }

//     // Public Complaints View
//     if (document.getElementById('complaintsContainer') && !window.location.pathname.includes('admin')) {
//         loadPublicComplaints();
//     }

//     // Index Scroll
//     if (document.getElementById('complaintsScroll')) {
//         loadRecentComplaints();
//     }
// });

// async function loadProfile() {
//     const res = await apiRequest('/users/me');
//     if (res && res.ok) {
//         const user = await res.json();
//         document.getElementById('userName').textContent = user.name;
//         document.getElementById('userEmail').textContent = user.email;
//         document.getElementById('userPhone').textContent = user.phone;
//         document.getElementById('userAddress').textContent = user.address || '-';
//         document.getElementById('userAge').textContent = user.age || '-';
//         document.getElementById('userGender').textContent = user.gender || '-';

//         // Fill edit form
//         document.getElementById('editName').value = user.name;
//         document.getElementById('editPhone').value = user.phone;
//         document.getElementById('editAddress').value = user.address || '';
//         document.getElementById('editAge').value = user.age || '';
//         document.getElementById('editGender').value = user.gender || '';
//     }
// }

// async function updateProfile() {
//     const body = {
//         name: document.getElementById('editName').value,
//         phone: document.getElementById('editPhone').value,
//         address: document.getElementById('editAddress').value,
//         age: parseInt(document.getElementById('editAge').value),
//         gender: document.getElementById('editGender').value
//     };

//     const res = await apiRequest('/users/me', 'PUT', body);
//     if (res && res.ok) {
//         alert('Profile updated');
//         document.getElementById('editForm').style.display = 'none';
//         document.getElementById('profileView').style.display = 'block';
//         loadProfile();
//     }
// }

// async function loadMyComplaints() {
//     const res = await apiRequest('/complaints/me');
//     if (res && res.ok) {
//         const complaints = await res.json();
//         const container = document.getElementById('myComplaints');
//         container.innerHTML = complaints.map(c => `
//             <div class="complaint-item" style="padding: 1rem; border-bottom: 1px solid #eee;">
//                 <h4>${c.title} <span class="status-badge status-${c.status}">${c.status}</span></h4>
//                 <p>${c.description}</p>
//                 <small>Dept: ${c.department_name}</small>
//             </div>
//         `).join('');
//     }
// }

// async function loadDepartments() {
//     // Seed first
//     await apiRequest('/departments/seed', 'POST');
//     const res = await apiRequest('/departments/');
//     if (res && res.ok) {
//         const depts = await res.json();
//         const grid = document.getElementById('departmentGrid');
//         grid.innerHTML = depts.map(d => `
//             <div class="dept-card" onclick="window.location.href='complaint.html?dept=${d.name}'">
//                 <h3>${d.name}</h3>
//                 <p>${d.description}</p>
//             </div>
//         `).join('');
//     }
// }

// async function loadRecentComplaints() {
//     const res = await apiRequest('/complaints/');
//     if (res && res.ok) {
//         const complaints = await res.json();
//         const container = document.getElementById('complaintsScroll');
//         // Show last 5
//         container.innerHTML = complaints.slice(0, 5).map(c => `
//             <div class="complaint-card">
//                 <h3>${c.department_name}</h3>
//                 <p>${c.title}</p>
//                 <span class="status-badge status-${c.status}">${c.status}</span>
//             </div>
//         `).join('');
//     }
// }

// async function loadPublicComplaints() {
//     const res = await apiRequest('/complaints/');
//     if (res && res.ok) {
//         const complaints = await res.json();
//         const container = document.getElementById('complaintsContainer');
//         container.innerHTML = complaints.map(c => `
//             <div class="card">
//                 <h3>${c.title}</h3>
//                 <p><strong>Dept:</strong> ${c.department_name}</p>
//                 <p>${c.description}</p>
//                 <span class="status-badge status-${c.status}">${c.status}</span>
//                 ${c.evidence_file ? `<a href="${API_URL}/${c.evidence_file}" target="_blank">View Evidence</a>` : ''}
//             </div>
//         `).join('');
//     }
// }

// // Admin functions
// async function loadAdminStats() {
//     const res = await apiRequest('/complaints/stats');
//     if (res && res.ok) {
//         const stats = await res.json();
//         document.getElementById('totalComplaints').textContent = stats.total;
//         document.getElementById('pendingComplaints').textContent = stats.pending;
//         document.getElementById('inProgressComplaints').textContent = stats.in_progress;
//         document.getElementById('solvedComplaints').textContent = stats.solved;
//     }
// }

// async function loadAllComplaintsAdmin() {
//     const res = await apiRequest('/complaints/'); // Admin sees all too
//     if (res && res.ok) {
//         const complaints = await res.json();
//         const container = document.getElementById('complaintsContainer');
//         container.innerHTML = complaints.map(c => `
//             <div class="card" style="border-left: 5px solid var(--primary);">
//                 <div style="display:flex; justify-content:space-between;">
//                     <h3>${c.title}</h3>
//                     <button class="btn btn-primary" onclick="openUpdateModal(${c.id})">Update Status</button>
//                 </div>
//                 <p><strong>Status:</strong> ${c.status}</p>
//                 <p>${c.description}</p>
//             </div>
//         `).join('');
//     }
// }

// // Exposed for onclick
// window.showEditForm = () => {
//     document.getElementById('profileView').style.display = 'none';
//     document.getElementById('editForm').style.display = 'block';
// };

// window.cancelEdit = () => {
//     document.getElementById('editForm').style.display = 'none';
//     document.getElementById('profileView').style.display = 'block';
// };

// let currentComplaintId = null;
// window.openUpdateModal = (id) => {
//     currentComplaintId = id;
//     document.getElementById('updateModal').style.display = 'block';
// };

// window.closeModal = () => {
//     document.getElementById('updateModal').style.display = 'none';
// };

// window.saveUpdate = async () => {
//     const status = document.getElementById('updateStatus').value;
//     const response = document.getElementById('updateResponse').value;

//     const res = await apiRequest(`/complaints/${currentComplaintId}/status`, 'PUT', {
//         status: status,
//         admin_response: response
//     });

//     if (res && res.ok) {
//         alert('Status updated');
//         closeModal();
//         loadAdminStats();
//         loadAllComplaintsAdmin();
//     }
// };

// window.logout = logout;
// window.adminLogout = adminLogout;
