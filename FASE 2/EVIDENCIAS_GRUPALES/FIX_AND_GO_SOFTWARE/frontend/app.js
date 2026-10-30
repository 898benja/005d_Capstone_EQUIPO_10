const API_URL = 'http://127.0.0.1:8000/api/v1';

// State
let state = {
    token: null,
    user: null
};

// DOM Elements
const app = document.getElementById('app');
const mainContent = document.getElementById('main-content');
const navLinks = document.getElementById('nav-links');

// Init
function init() {
    renderNav();
    if (state.token) {
        renderDashboard();
    } else {
        renderLogin();
    }
}

// Render Functions
function renderNav() {
    if (state.token) {
        navLinks.replaceChildren();
        const identity = document.createElement('span');
        identity.className = 'text-sm text-muted mr-4';
        identity.textContent = `${state.user.email} (${state.user.role_display})`;
        const exit = document.createElement('a');
        exit.textContent = 'Cerrar sesión';
        exit.addEventListener('click', logout);
        navLinks.append(identity, exit);
    } else {
        navLinks.innerHTML = ``;
    }
}

function renderLogin() {
    const template = document.getElementById('tpl-login').content.cloneNode(true);
    mainContent.innerHTML = '';
    mainContent.appendChild(template);

    const form = document.getElementById('login-form');
    form.addEventListener('submit', handleLogin);
}

async function renderDashboard() {
    const template = document.getElementById('tpl-dashboard').content.cloneNode(true);
    mainContent.innerHTML = '';
    mainContent.appendChild(template);

    document.getElementById('user-name').textContent = state.user.first_name || state.user.email.split('@')[0];

    // Fetch data concurrently
    fetchProviders();
    fetchRequests();
}

// Handlers
async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const errorDiv = document.getElementById('login-error');

    try {
        const res = await fetch(`${API_URL}/auth/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await res.json();

        if (res.ok) {
            state.token = data.token;
            state.user = data.user;
            // Sesión solo en memoria para este prototipo web heredado.
            init();
        } else {
            errorDiv.textContent = data.non_field_errors?.[0] || 'Credenciales inválidas';
        }
    } catch (err) {
        errorDiv.textContent = 'Error de conexión con el servidor';
        console.error(err);
    }
}

async function logout() {
    const token = state.token;
    if (token) {
        try { await fetch(`${API_URL}/auth/logout/`, {method: 'POST', headers: {Authorization: `Token ${token}`}}); }
        catch { /* La sesión local se cierra incluso sin conexión. */ }
    }
    state.token = null;
    state.user = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    init();
}

// Data Fetching
async function apiGet(endpoint) {
    const res = await fetch(`${API_URL}${endpoint}`, {
        headers: {
            'Authorization': `Token ${state.token}`
        }
    });
    if (!res.ok) {
        if (res.status === 401) await logout();
        throw new Error('API Error');
    }
    return res.json();
}

async function allPages(endpoint) {
    const rows = [];
    for (let page = 1; page <= 100; page++) {
        const result = await apiGet(`${endpoint}?page=${page}`);
        rows.push(...result.results);
        if (!result.next) return rows;
    }
    throw new Error('Demasiados registros');
}

async function fetchProviders() {
    const container = document.getElementById('providers-list');
    try {
        const providers = await allPages('/providers/');
        container.innerHTML = '';

        if (providers.length === 0) {
            container.innerHTML = '<p class="text-muted">No hay prestadores disponibles.</p>';
            return;
        }

        providers.forEach(p => {
            const tpl = document.getElementById('tpl-provider-card').content.cloneNode(true);
            tpl.querySelector('.provider-name').textContent = p.display_name;
            tpl.querySelector('.provider-desc').textContent = p.description;
            tpl.querySelector('.experience').textContent = `${p.years_experience} años exp.`;
            tpl.querySelector('.phone').textContent = p.phone;

            const catContainer = tpl.querySelector('.provider-categories');
            p.categories.forEach(cat => {
                const span = document.createElement('span');
                span.className = 'tag';
                span.textContent = cat.name;
                catContainer.appendChild(span);
            });

            container.appendChild(tpl);
        });
    } catch (e) {
        container.innerHTML = '<p class="error-message">Error cargando prestadores.</p>';
    }
}

async function fetchRequests() {
    const container = document.getElementById('requests-list');
    try {
        const requests = await allPages('/requests/');
        container.innerHTML = '';

        if (requests.length === 0) {
            container.innerHTML = '<p class="text-muted">No tienes solicitudes activas.</p>';
            return;
        }

        requests.forEach(r => {
            const tpl = document.getElementById('tpl-request-card').content.cloneNode(true);
            tpl.querySelector('.request-category').textContent = r.category_name;
            tpl.querySelector('.status').textContent = translateStatus(r.status);
            tpl.querySelector('.request-desc').textContent = r.description;
            tpl.querySelector('.client-name').textContent = r.client_name;
            tpl.querySelector('.provider-name').textContent = r.provider_name;
            tpl.querySelector('.commune').textContent = r.commune_name;
            tpl.querySelector('.date').textContent = new Date(r.created_at).toLocaleDateString('es-CL');

            container.appendChild(tpl);
        });
    } catch (e) {
        container.innerHTML = '<p class="error-message">Error cargando solicitudes.</p>';
    }
}

function translateStatus(status) {
    const map = {
        'PENDING': 'Pendiente',
        'QUOTED': 'Cotizada',
        'ACCEPTED': 'Aceptada',
        'REJECTED': 'Rechazada',
        'CANCELLED': 'Cancelada'
    };
    return map[status] || status;
}

// Start app
document.addEventListener('DOMContentLoaded', init);
