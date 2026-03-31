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
        loadDashboardStats();
        loadAuditLogs();
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
    
    const formData = new URLSearchParams();
    formData.append('username', email); // OAuth2 expects 'username'
    formData.append('password', password);

    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });
        const data = await res.json();
        if (res.ok) {
            token = data.access_token;
            localStorage.setItem('token', token);
            // Recover user info since the route doesn't return it directly now
            await validateToken();
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
    const orderJsonInput = document.getElementById('orderJson').value;
    const msg = document.getElementById('ticketMsg');
    
    let order_json;
    try {
        order_json = JSON.parse(orderJsonInput);
    } catch (e) {
        msg.textContent = 'Invalid Order Metadata JSON structure';
        return;
    }
    
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
            // Refresh Log
            loadAuditLogs();
        } else {
            msg.textContent = 'Auth Required / Submission failed';
        }
    } catch (err) {
        msg.textContent = 'Agent synchronization error';
    }
});

async function loadDashboardStats() {
    if (!token) return;
    try {
        const res = await fetch('/api/ticket/stats', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (res.ok) {
            const statCards = document.querySelectorAll('.stat-card');
            if (statCards.length >= 3) {
                statCards[0].querySelector('.value').textContent = data.total_audits.toLocaleString();
                statCards[1].querySelector('.value').textContent = data.compliance_rate;
                statCards[2].querySelector('.value').textContent = data.avg_latency;
            }

            // Render Activity Chart
            const chart = document.getElementById('activityIndicator');
            if (chart && data.activity) {
                const max = Math.max(...data.activity.map(a => a.count)) || 1;
                chart.innerHTML = `<div class="bars">${data.activity.map(a => `
                    <div class="bar" style="height: ${Math.max(5, (a.count / max) * 100)}%;">
                        <span class="bar-label">${a.day}</span>
                    </div>`).join('')}</div>`;
            }
        }
    } catch (err) {
        console.error('Stats sync error');
    }
}

async function loadAuditLogs() {
    const container = document.getElementById('responsesContent');
    if (!container) return;

    try {
        const res = await fetch('/api/ticket/history', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (res.ok && data.length > 0) {
            container.innerHTML = data.map(item => `
                <div class="audit-item glass">
                    <div class="audit-meta">
                        <span class="tag live">${item.category.toUpperCase()}</span>
                        <p>${item.ticket_text.substring(0, 50)}...</p>
                    </div>
                    <div class="audit-action">
                        <span class="tag ${item.decision.toLowerCase()}">${item.decision}</span>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<p class="placeholder-empty">No resolution logs found.</p>';
        }
    } catch (err) {
        container.innerHTML = '<p>History sync error.</p>';
    }
}

document.getElementById('loadResponses')?.addEventListener('click', loadAuditLogs);

// Knowledge Sync (Hardened for Production)
document.getElementById('uploadForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.currentTarget;
    const fileInput = document.getElementById('policyFile');
    const msg = document.getElementById('uploadMsg');
    
    // Safety check for UI elements
    if (!fileInput || !msg) {
        console.error("Critical: Policy Sync Elements Missing from DOM.", { fileInput, msg });
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
        dropZone.style.background = 'rgba(139, 92, 246, 0.1)';
    });
    dropZone.addEventListener('dragleave', () => {
        dropZone.style.borderColor = 'var(--glass-border)';
        dropZone.style.background = 'transparent';
    });
    
    const updateDropZoneUI = (file) => {
        dropZone.innerHTML = `<i data-lucide="file-check"></i><h3>${file.name}</h3><p>Source document ready.</p>`;
        initIcons();
    };

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        if (e.dataTransfer.files.length > 0) {
            fileInput.files = e.dataTransfer.files;
            updateDropZoneUI(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            updateDropZoneUI(fileInput.files[0]);
        }
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
        const res = await fetch('/api/evaluation/run', { 
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) throw new Error('Unauthorized or Server Error');
        
        const data = await res.json();
        
        metrics.style.display = 'flex';
        document.getElementById('metricCorrectness').textContent = `${(data.summary.correctness_rate * 100).toFixed(1)}%`;
        
        content.innerHTML = data.results.map(r => `
            <div class="audit-item glass">
                <div class="audit-meta">
                    <h4>Case #${r.case_id}</h4>
                    <p style="font-size: 0.85rem; color: var(--text-dim);">${r.ticket_text.substring(0, 100)}...</p>
                    <div style="margin-top: 0.5rem; font-size: 0.8rem; color: var(--primary);">Expected: ${r.expected.decision} | Result: ${r.result.decision}</div>
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
