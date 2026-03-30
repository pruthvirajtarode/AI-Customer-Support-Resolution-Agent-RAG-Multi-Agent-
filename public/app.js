// State Management
let token = localStorage.getItem('token');
let currentUser = null;

// Initialize Lucide Icons
function initIcons() {
    if (window.lucide) {
        window.lucide.createIcons();
    }
}

// Navigation Handling
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
        const targetId = item.getAttribute('data-target');
        if (targetId) {
            e.preventDefault();
            showPanel(targetId);
            
            // Update Active State
            document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            
            // Push state for browser back button
            window.location.hash = targetId;
        }
    });
});

function showPanel(panelId) {
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    const targetPanel = document.getElementById(panelId);
    if (targetPanel) {
        targetPanel.classList.add('active');
    }
    initIcons();
}

// Authentication UI Updates
async function validateToken() {
    if (!token) return updateAuthUI(null);
    
    try {
        const res = await fetch('/api/auth/me', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
            const user = await res.json();
            updateAuthUI(user);
        } else {
            token = null;
            localStorage.removeItem('token');
            updateAuthUI(null);
        }
    } catch (err) {
        updateAuthUI(null);
    }
}

function updateAuthUI(user) {
    const userDisplay = document.getElementById('user-display');
    const authButtons = document.getElementById('auth-buttons');
    
    if (user) {
        currentUser = user;
        userDisplay.querySelector('.user-name').textContent = user.full_name;
        userDisplay.style.display = 'flex';
        authButtons.style.display = 'none';
        if (window.location.hash === '#login' || window.location.hash === '#signup' || !window.location.hash) {
            showPanel('dashboard');
        }
    } else {
        currentUser = null;
        userDisplay.style.display = 'none';
        authButtons.style.display = 'block';
        if (window.location.hash !== '#signup') {
            showPanel('login');
        }
    }
    initIcons();
}

// Logout Handling
document.getElementById('sidebar-logout')?.addEventListener('click', () => {
    token = null;
    localStorage.removeItem('token');
    updateAuthUI(null);
});

// Auth Form Submissions
document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const msg = document.getElementById('loginMsg');
    
    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        if (res.ok) {
            token = data.access_token;
            localStorage.setItem('token', token);
            updateAuthUI(data.user);
            msg.innerHTML = '<span class="tag live">Authenticated</span>';
        } else {
            msg.textContent = data.detail || 'Login failed';
        }
    } catch (err) {
        msg.textContent = 'Server connection error';
    }
});

document.getElementById('signupForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const full_name = document.getElementById('signupName').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    const msg = document.getElementById('signupMsg');
    
    try {
        const res = await fetch('/api/auth/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, full_name })
        });
        const data = await res.json();
        if (res.ok) {
            msg.innerHTML = '<span class="tag live">Account Created!</span>';
            setTimeout(() => showPanel('login'), 2000);
        } else {
            msg.textContent = data.detail || 'Registration failed';
        }
    } catch (err) {
        msg.textContent = 'Server connection error';
    }
});

// Ticket Submission
document.getElementById('ticketForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = document.getElementById('ticketText').value;
    const order_json = JSON.parse(document.getElementById('orderJson').value);
    const msg = document.getElementById('ticketMsg');
    
    msg.innerHTML = '<div class="system-status"><div class="status-dot"></div><span>AI Cluster Synchronizing...</span></div>';
    
    try {
        const res = await fetch('/api/ticket/audit', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ text, order_json })
        });
        const data = await res.json();
        if (res.ok) {
            msg.innerHTML = `
                <div class="card glass" style="margin-top: 1.5rem; border-left: 4px solid var(--primary);">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                        <span class="tag live">${data.triage_result.category.toUpperCase()}</span>
                        <span class="tag ${data.resolution.decision.toLowerCase()}">${data.resolution.decision}</span>
                    </div>
                    <p style="font-size: 0.95rem; line-height: 1.6;">${data.resolution.explanation}</p>
                </div>
            `;
        } else {
            msg.textContent = 'Auth Required / Submission failed';
        }
    } catch (err) {
        msg.textContent = 'Agent synchronization error';
    }
});

// Knowledge Sync (Hardened for Production)
document.getElementById('uploadForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.currentTarget;
    const fileInput = form.querySelector('#policyFile');
    const msg = document.getElementById('uploadMsg');
    
    // Safety check for UI elements
    if (!fileInput || !msg) {
        console.error("Critical: Policy Sync Elements Missing.");
        return;
    }

    if (!token) {
        msg.innerHTML = '<span class="tag deny">Login Token Required</span>';
        setTimeout(() => showPanel('login'), 1500);
        return;
    }

    if (!fileInput.files || fileInput.files.length === 0) {
        msg.innerHTML = '<span class="tag orange">Select a policy source file</span>';
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);
    
    msg.innerHTML = '<div class="system-status"><div class="status-dot"></div><span>Vector Indexing in progress...</span></div>';
    
    try {
        const res = await fetch('/api/policy/sync', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
        });
        const data = await res.json();
        if (res.ok) {
            msg.innerHTML = `<span class="tag live">Index Ready: ${data.indexed_chunks || 0} Nodes</span>`;
        } else {
            msg.innerHTML = `<span class="tag deny">Sync Failure: ${data.detail || 'Access Denied'}</span>`;
        }
    } catch (err) {
        msg.innerHTML = '<span class="tag deny">Cloud Connectivity Error</span>';
    }
});

// Drop Zone Interaction
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('policyFile');

if (dropZone && fileInput) {
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--primary)';
    });
    dropZone.addEventListener('dragleave', () => dropZone.style.borderColor = 'var(--glass-border)');
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        fileInput.files = e.dataTransfer.files;
        dropZone.innerHTML = `<i data-lucide="file-check"></i><h3>${e.dataTransfer.files[0].name}</h3><p>Ready for AI indexing</p>`;
        initIcons();
    });
}

// Evaluation Engine
document.getElementById('runEvaluation')?.addEventListener('click', async () => {
    const btn = document.getElementById('runEvaluation');
    const content = document.getElementById('evaluationContent');
    const metrics = document.getElementById('evaluationMetrics');
    
    btn.disabled = true;
    btn.innerHTML = '<i data-lucide="loader" class="spin"></i> Running Baseline...';
    initIcons();

    try {
        const res = await fetch('/api/evaluation/run', { method: 'POST' });
        const data = await res.json();
        
        metrics.style.display = 'flex';
        document.getElementById('metricCorrectness').textContent = `${(data.summary.correctness_rate * 100).toFixed(1)}%`;
        
        content.innerHTML = data.results.map(r => `
            <div class="audit-item glass">
                <div class="audit-meta">
                    <h4>Case #${r.case_id}</h4>
                    <p>${r.ticket_text.substring(0, 70)}...</p>
                </div>
                <div class="audit-action">
                    <span class="tag ${r.is_correct ? 'live' : 'deny'}">${r.is_correct ? 'PASSED' : 'FAIL'}</span>
                </div>
            </div>
        `).join('');
    } catch (err) {
        content.innerHTML = '<p>Engine connection timeout.</p>';
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i data-lucide="gauge"></i> Start Baseline Audit';
        initIcons();
    }
});

// Initial Load
document.addEventListener('DOMContentLoaded', () => {
    initIcons();
    const hash = window.location.hash.substring(1) || 'dashboard';
    showPanel(hash);
    validateToken();
});

window.addEventListener('hashchange', () => {
    const hash = window.location.hash.substring(1) || 'dashboard';
    showPanel(hash);
});
