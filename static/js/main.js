// EduHub - Minimal JS utilities (most logic is inline in each template)
// This file is kept for shared utilities if needed.

function getToken() {
    return localStorage.getItem('eduhub_token');
}

function getUser() {
    try {
        return JSON.parse(localStorage.getItem('eduhub_user'));
    } catch {
        return null;
    }
}

function logout() {
    localStorage.removeItem('eduhub_token');
    localStorage.removeItem('eduhub_user');
    window.location.href = '/login';
}

async function authFetch(url, options = {}) {
    const token = getToken();
    if (!token) {
        window.location.href = '/login';
        return;
    }
    options.headers = options.headers || {};
    options.headers['Authorization'] = 'Bearer ' + token;
    return fetch(url, options);
}

function requireAuth() {
    if (!getToken()) {
        window.location.href = '/login';
        return false;
    }
    return true;
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.style.cssText = `position:fixed; bottom:20px; right:20px; padding:14px 24px; border-radius:12px; color:white; font-weight:600; z-index:1000; font-size:14px; animation:fadeIn 0.5s ease; background:${type === 'success' ? '#55D6BE' : '#ff6b6b'}; color:${type === 'success' ? '#32292F' : 'white'};`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.5s';
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}