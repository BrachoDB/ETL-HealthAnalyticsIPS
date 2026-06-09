export const api = (() => {
const BASE = '';


  function getHeaders() {
    const token = localStorage.getItem('ha_access_token');
    const h = {
      'Content-Type': 'application/json'
    };
    if (token) h['Authorization'] = `Bearer ${token}`;
    return h;
  }

  function setToken(token) {
    localStorage.setItem('ha_access_token', token);
  }

  function clearToken() {
    localStorage.removeItem('ha_access_token');
  }

  async function request(path, { method = 'GET', body = null, headers = {} } = {}) {
    const res = await fetch(`${BASE}${path}`,
      {
        method,
        headers: { ...getHeaders(), ...headers },
        body: body ? (typeof body === 'string' ? body : JSON.stringify(body)) : null,
      }
    );

    let data;
    const text = await res.text();
    try { data = text ? JSON.parse(text) : null; } catch { data = text; }

    if (!res.ok) {
      const err = data && typeof data === 'object' ? data : { detail: data };
      throw err;
    }
    return data;
  }

  async function login(payload) {
    // login is outside token-protected endpoints
    const res = await fetch(`${BASE}auth/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const text = await res.text();
    const data = text ? JSON.parse(text) : {};
    if (!res.ok) {
      throw data;
    }
    return data;
  }

  async function getDashboardKpis() {
    return request('api/dashboard/dashboard/kpis/', { method: 'GET' });
  }


  async function getPacientes(queryString = '') {
    const qs = queryString ? `?${queryString}` : '';
    return request(`etl/pacientes/${qs}`, { method: 'GET' });
  }

  async function runEtl(file) {
    const token = localStorage.getItem('ha_access_token');
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {};

    const form = new FormData();
    if (file) form.append('file', file);

    const res = await fetch(`${BASE}etl/etl/run/`, {
      method: 'POST',
      headers,
      body: form
    });

    const text = await res.text();
    let data;
    try { data = text ? JSON.parse(text) : null; } catch { data = text; }
    if (!res.ok) throw (data || { detail: text });
    return data;
  }

  async function predict({ inputs }) {
    return request('ml/predicciones/', { method: 'POST', body: { inputs } });
  }

  async function getReports() {
    return request('api/reports/reportes/', { method: 'GET' });
  }

  async function getAnalyticsStats() {
    return request('api/analytics/analytics-stats/', { method: 'GET' });
  }

  async function getAnalyticsStats2() {
    return request('api/analytics/analytics-stats/', { method: 'GET' });
  }


  return {
    login,
    setToken,
    clearToken,
    getDashboardKpis,
    getPacientes,
    runEtl,
    predict,
    getReports,
    getAnalyticsStats,
    getAnalyticsStats2,
  };
})();

