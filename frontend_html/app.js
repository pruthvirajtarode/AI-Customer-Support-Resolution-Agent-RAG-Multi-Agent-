// SPA navigation
const panels = document.querySelectorAll('.panel');
function showPanel(hash) {
    panels.forEach(p => p.classList.remove('active'));
    const panel = document.querySelector(hash);
    if (panel) panel.classList.add('active');
}
window.addEventListener('hashchange', () => showPanel(location.hash));
window.addEventListener('DOMContentLoaded', () => {
    showPanel(location.hash || '#login');
});

const API_URL = 'http://localhost:8000';
let token = localStorage.getItem('token') || '';

// Login
const loginForm = document.getElementById('loginForm');
if (loginForm) loginForm.onsubmit = async e => {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const res = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`
    });
    const data = await res.json();
    if (res.ok) {
        token = data.access_token;
        localStorage.setItem('token', token);
        document.getElementById('loginMsg').textContent = 'Login successful!';
        location.hash = '#dashboard';
    } else {
        document.getElementById('loginMsg').textContent = data.detail || 'Login failed.';
    }
};

// Signup
const signupForm = document.getElementById('signupForm');
if (signupForm) signupForm.onsubmit = async e => {
    e.preventDefault();
    const name = document.getElementById('signupName').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    const res = await fetch(`${API_URL}/auth/register?name=${encodeURIComponent(name)}&email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`, {
        method: 'POST'
    });
    const data = await res.json();
    document.getElementById('signupMsg').textContent = data.msg || data.detail || 'Signup failed.';
    if (res.ok) location.hash = '#login';
};

// Upload Policy
const uploadForm = document.getElementById('uploadForm');
if (uploadForm) uploadForm.onsubmit = async e => {
    e.preventDefault();
    const fileInput = document.getElementById('policyFile');
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_URL}/policy/upload`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
    });
    const data = await res.json();
    document.getElementById('uploadMsg').textContent = data.msg || data.detail || 'Upload failed.';
};

// Submit Ticket
const ticketForm = document.getElementById('ticketForm');
if (ticketForm) ticketForm.onsubmit = async e => {
    e.preventDefault();
    const ticketText = document.getElementById('ticketText').value;
    const orderJson = document.getElementById('orderJson').value;
    const res = await fetch(`${API_URL}/ticket/submit?ticket_text=${encodeURIComponent(ticketText)}&order_json=${encodeURIComponent(orderJson)}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await res.json();
    document.getElementById('ticketMsg').textContent = JSON.stringify(data, null, 2);
};

// Load Responses
const loadResponsesBtn = document.getElementById('loadResponses');
if (loadResponsesBtn) loadResponsesBtn.onclick = async () => {
    const res = await fetch(`${API_URL}/ticket/responses`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await res.json();
    document.getElementById('responsesContent').textContent = JSON.stringify(data, null, 2);
};
