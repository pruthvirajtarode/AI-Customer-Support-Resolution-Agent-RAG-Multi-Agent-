// SPA navigation
const panels = document.querySelectorAll('.panel');
const navLinks = {
    '#login': 'nav-login',
    '#signup': 'nav-signup',
    '#dashboard': 'nav-dashboard',
    '#upload': 'nav-upload',
    '#ticket': 'nav-ticket',
    '#responses': 'nav-responses',
    '#evaluation': 'nav-evaluation'
};

function showPanel(hash) {
    hash = hash || '#login';
    panels.forEach(p => p.classList.remove('active'));
    document.querySelectorAll('nav li').forEach(li => li.style.opacity = '0.6');
    
    const panel = document.querySelector(hash);
    if (panel) panel.classList.add('active');
    
    const navId = navLinks[hash];
    if (navId) document.getElementById(navId).style.opacity = '1';
}

window.addEventListener('hashchange', () => showPanel(location.hash));

const API_URL = '/api';
let token = localStorage.getItem('token') || '';

function updateDashboardUI() {
    if (token) {
        document.getElementById('nav-login').style.display = 'none';
        document.getElementById('nav-signup').style.display = 'none';
        document.getElementById('nav-dashboard').style.display = 'block';
        document.getElementById('nav-upload').style.display = 'block';
        document.getElementById('nav-ticket').style.display = 'block';
        document.getElementById('nav-responses').style.display = 'block';
        document.getElementById('nav-evaluation').style.display = 'block';
    } else {
        document.getElementById('nav-login').style.display = 'block';
        document.getElementById('nav-signup').style.display = 'block';
        document.getElementById('nav-dashboard').style.display = 'none';
        document.getElementById('nav-upload').style.display = 'none';
        document.getElementById('nav-ticket').style.display = 'none';
        document.getElementById('nav-responses').style.display = 'none';
        document.getElementById('nav-evaluation').style.display = 'none';
    }
}

window.addEventListener('DOMContentLoaded', () => {
    updateDashboardUI();
    showPanel(location.hash);
    if (window.lucide) lucide.createIcons();
});

// Login
const loginForm = document.getElementById('loginForm');
if (loginForm) loginForm.onsubmit = async e => {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const btn = loginForm.querySelector('button');
    btn.textContent = 'Authenticating...';
    
    try {
        const res = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`
        });
        const data = await res.json();
        if (res.ok) {
            token = data.access_token;
            localStorage.setItem('token', token);
            updateDashboardUI();
            location.hash = '#dashboard';
        } else {
            document.getElementById('loginMsg').innerHTML = `<span style="color: #ef4444;">${data.detail || 'Login failed.'}</span>`;
        }
    } catch (err) {
        document.getElementById('loginMsg').textContent = 'Connection error.';
    } finally {
        btn.textContent = 'Sign In';
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
    if (res.ok) {
        document.getElementById('signupMsg').innerHTML = `<span style="color: #10b981;">Account created! Redirecting...</span>`;
        setTimeout(() => location.hash = '#login', 1500);
    } else {
        document.getElementById('signupMsg').innerHTML = `<span style="color: #ef4444;">${data.detail || 'Signup failed.'}</span>`;
    }
};

// Upload Policy
const uploadForm = document.getElementById('uploadForm');
if (uploadForm) uploadForm.onsubmit = async e => {
    e.preventDefault();
    const fileInput = document.getElementById('policyFile');
    const file = fileInput.files[0];
    const btn = uploadForm.querySelector('button');
    btn.textContent = 'Syncing Knowledge...';
    
    const formData = new FormData();
    formData.append('file', file);
    try {
        const res = await fetch(`${API_URL}/policy/upload`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
        });
        const data = await res.json();
        if (res.ok) {
            document.getElementById('uploadMsg').innerHTML = `<span style="color: #10b981;">${data.msg}</span>`;
        } else {
            document.getElementById('uploadMsg').innerHTML = `<span style="color: #ef4444;">${data.detail}</span>`;
        }
    } catch (err) {
        document.getElementById('uploadMsg').textContent = 'Upload failed.';
    } finally {
        btn.textContent = 'Sync Knowledge Base';
    }
};

// Submit Ticket
const ticketForm = document.getElementById('ticketForm');
if (ticketForm) ticketForm.onsubmit = async e => {
    e.preventDefault();
    const ticketText = document.getElementById('ticketText').value;
    const orderJson = document.getElementById('orderJson').value;
    const btn = ticketForm.querySelector('button');
    btn.textContent = 'Agent Pipeline Running...';
    
    try {
        const res = await fetch(`${API_URL}/ticket/submit?ticket_text=${encodeURIComponent(ticketText)}&order_json=${encodeURIComponent(orderJson)}`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        const msgDiv = document.getElementById('ticketMsg');
        msgDiv.innerHTML = `
            <div class="response-card" style="margin-top: 2rem;">
                <span class="tag ${data.decision}">${data.decision}</span>
                <p style="font-weight: 600; margin-bottom: 0.5rem;">AI Response:</p>
                <p style="color: var(--text-main); line-height: 1.6;">${data.customer_response}</p>
                <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--glass-border);">
                    <p style="font-size: 0.8rem; color: var(--text-muted);"><strong>Rationale:</strong> ${data.rationale}</p>
                </div>
            </div>
        `;
    } catch (err) {
        document.getElementById('ticketMsg').textContent = 'Error processing ticket.';
    } finally {
        btn.textContent = 'Run Resolution Pipeline';
    }
};

// Load Responses
const loadResponsesBtn = document.getElementById('loadResponses');
if (loadResponsesBtn) loadResponsesBtn.onclick = async () => {
    const content = document.getElementById('responsesContent');
    content.innerHTML = '<p>Loading history...</p>';
    try {
        const res = await fetch(`${API_URL}/ticket/responses`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (data.length === 0) {
            content.innerHTML = '<p style="color: var(--text-muted);">No resolutions found.</p>';
            return;
        }
        content.innerHTML = data.map(r => `
            <div class="response-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <span class="tag ${r.decision}">${r.decision}</span>
                    <span style="font-size: 0.7rem; color: var(--text-muted);">${new Date(r.created_at).toLocaleString()}</span>
                </div>
                <p style="margin: 1rem 0;">${r.response_text}</p>
                <p style="font-size: 0.8rem; color: var(--text-muted);"><strong>Category:</strong> ${r.classification}</p>
            </div>
        `).join('');
    } catch (err) {
        content.innerHTML = 'Failed to load responses.';
    }
};

// Run Evaluation
const runEvalBtn = document.getElementById('runEvaluation');
if (runEvalBtn) runEvalBtn.onclick = async () => {
    const btn = runEvalBtn;
    const statsDiv = document.getElementById('evaluationMetrics');
    const content = document.getElementById('evaluationContent');
    
    btn.textContent = 'Running 20+ Test Audit...';
    btn.disabled = true;
    statsDiv.style.display = 'none';
    content.innerHTML = '<p>Processing evaluation cases, please wait...</p>';

    try {
        const res = await fetch(`${API_URL}/evaluation/report`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        
        // Show Metrics
        statsDiv.style.display = 'grid';
        document.getElementById('metricCorrectness').textContent = data.correctness;
        document.getElementById('metricCoverage').textContent = data.citation_coverage;
        document.getElementById('metricEscalation').textContent = data.escalation_accuracy;

        // Show Details
        content.innerHTML = data.details.map(item => `
            <div class="response-card" style="border-left: 4px solid ${item.correct ? '#10b981' : '#ef4444'};">
                <p style="font-size: 0.8rem; font-weight: 700; opacity: 0.7;">Case # ${item.input.ticket_text.substring(0, 30)}...</p>
                <div style="display: flex; gap: 1rem; margin-top: 0.5rem;">
                    <div style="flex: 1;">
                        <span style="font-size: 0.7rem; color: var(--text-muted);">EXPECTED</span>
                        <div style="font-size: 0.8rem; font-weight: 600;">Decision: ${item.input.expected.decision}</div>
                    </div>
                    <div style="flex: 1;">
                        <span style="font-size: 0.7rem; color: var(--text-muted);">ACTUAL</span>
                        <div style="font-size: 0.8rem; font-weight: 600; color: ${item.correct ? '#10b981' : '#f87171'};">Decision: ${item.output.decision}</div>
                    </div>
                </div>
                ${!item.correct ? `
                    <div style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px dashed var(--glass-border); font-size: 0.7rem; color: #f87171;">
                        Mismatch: AI decided to ${item.output.decision} instead of ${item.input.expected.decision}.
                    </div>
                ` : ''}
            </div>
        `).join('');

    } catch (err) {
        content.innerHTML = 'Evaluation failed. Make sure your backend with the 20 test cases is running.';
    } finally {
        btn.textContent = 'Run 20+ Case Audit';
        btn.disabled = false;
    }
};
