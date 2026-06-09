const form = document.getElementById('login-form');
const errorEl = document.getElementById('login-error');

function setError(msg) {
  if (!errorEl) return;
  errorEl.textContent = msg || '';
  errorEl.style.display = msg ? 'block' : 'none';
}

if (form) {
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    setError('');

    const username = form.elements['username'].value;
    const password = form.elements['password'].value;

    try {
      const data = await window.api.loginRequest(username, password);
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      window.location.href = '/dashboard/kpis/';
    } catch (err) {
      setError(String(err.message || err));
    }
  });
}

// logout
const btnLogout = document.getElementById('btn-logout');
if (btnLogout) {
  btnLogout.addEventListener('click', () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/';
  });
}

