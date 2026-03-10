// config.js - Shared configuration for all pages

const API_BASE_URL = "http://localhost:8000/api";

const DEPARTMENTS = [
    "Agriculture Department",
    "Finance Department",
    "Health and Family Welfare Department",
    "School Education Department",
    "Public Works Department",
    "Animal Husbandry, Dairying and Fisheries Department"
];

const DISTRICTS = [
    "Chennai", "Chengalpattu", "Kanchipuram", "Vellore",
    "Ranipet", "Tirupattur", "Tiruvannamalai", "Krishnagiri",
    "Dharmapuri", "Kallakurichi", "Villupuram"
];

const SUBCATEGORIES = {
    "Agriculture Department":    ["Crop Damage", "Irrigation Issue", "Fertilizer Problem", "Land Dispute", "Other"],
    "Finance Department":        ["Tax Issue", "Subsidy Problem", "Loan Issue", "Pension Problem", "Other"],
    "Health and Family Welfare Department": ["Hospital Facility", "Medicine Shortage", "Doctor Availability", "Ambulance Issue", "Other"],
    "School Education Department": ["Teacher Shortage", "Infrastructure", "Mid-Day Meal", "Scholarship Issue", "Other"],
    "Public Works Department":   ["Road Damage", "Bridge Issue", "Drainage Problem", "Street Light", "Other"],
    "Animal Husbandry, Dairying and Fisheries Department": ["Cattle Disease", "Fishing License", "Feed Shortage", "Veterinary Issue", "Other"]
};

// ─── Auth Helpers ─────────────────────────────────────────

function getToken()    { return localStorage.getItem("access_token"); }
function getUserRole() { return localStorage.getItem("role"); }
function getUserEmail(){ return localStorage.getItem("user_email"); }
function getUserName() { return localStorage.getItem("user_name"); }
function isLoggedIn()  { return !!getToken(); }

function logout() {
    const role = getUserRole();
    localStorage.clear();
    if (role === 'c_admin' || role === 'cm_admin') {
        window.location.href = './admin_login.html';
    } else {
        window.location.href = './index.html';
    }
}

function authHeader() {
    return { "Authorization": `Bearer ${getToken()}` };
}

// ─── Status Badge Helper ──────────────────────────────────

function statusBadge(status) {
    const map = {
        pending:             { label: "Pending",            color: "#F39C12" },
        under_investigation: { label: "Under Investigation",color: "#2980B9" },
        resolved:            { label: "Resolved",           color: "#27AE60" },
        rejected:            { label: "Rejected",           color: "#E74C3C" },
        solved:              { label: "Solved",             color: "#8E44AD" }
    };
    const s = map[status] || { label: status, color: "#95A5A6" };
    return `<span class="status-badge" style="background:${s.color}">${s.label}</span>`;
}

// ─── Date Format Helper ───────────────────────────────────

function formatDate(dateStr) {
    if (!dateStr) return "";
    return new Date(dateStr).toLocaleDateString("en-IN", {
        day: "2-digit", month: "short", year: "numeric"
    });
}
