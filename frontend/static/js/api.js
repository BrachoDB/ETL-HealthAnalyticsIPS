function getAccessToken() {
  return localStorage.getItem('access_token') || '';
}

function getHeaders() {
  const token = getAccessToken();
  const headers = {
    'Content-Type': 'application/json'
  };
  if (token) headers['Authorization'] = 'Bearer ' + token;
  return headers;
}

async function apiFetch(url, { method = 'GET', body = null, headers = {} } = {}) {
  const res = await fetch(url, {
    method,
    headers: { ...getHeaders(), ...headers },
    body: body ? JSON.stringify(body) : null,
  });

  const contentType = res.headers.get('content-type') || '';
  const isJson = contentType.includes('application/json');

  if (!res.ok) {
    const msg = isJson ? JSON.stringify(await res.json()) : await res.text();
    throw new Error(msg || ('HTTP ' + res.status));
  }

  return isJson ? await res.json() : await res.text();
}

async function loginRequest(username, password) {
  const res = await fetch('/api/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || data.error || 'Login failed');
  return data;
}

window.api = {
  apiFetch,
  loginRequest,
};

