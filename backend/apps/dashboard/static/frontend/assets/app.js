import { api } from './api.js';
import { charts } from './charts.js';


const els = {
  content: document.getElementById('content'),
  views: () => Array.from(document.querySelectorAll('[data-view]')),
  crumb: document.getElementById('crumb'),
  userPill: document.getElementById('userPill'),
  btnTheme: document.getElementById('btnTheme'),
  btnLogout: document.getElementById('btnLogout'),

  loginForm: document.getElementById('loginForm'),
  loginHint: document.getElementById('loginHint'),

  // KPIs
  kpi_total: document.getElementById('kpi_total'),
  kpi_critical: document.getElementById('kpi_critical'),
  kpi_avg_risk: document.getElementById('kpi_avg_risk'),
  kpi_pred_realizadas: document.getElementById('kpi_pred_realizadas'),
  kpi_etls: document.getElementById('kpi_etls'),
  kpi_diabetic: document.getElementById('kpi_diabetic'),
  kpi_hypertensive: document.getElementById('kpi_hypertensive'),

  // Pacientes
  btnLoadPacientes: document.getElementById('btnLoadPacientes'),
  tblPacientes: document.getElementById('tblPacientes'),
  pacientesMeta: document.getElementById('pacientesMeta'),
  f_riesgo: document.getElementById('f_riesgo'),
  f_sexo: document.getElementById('f_sexo'),
  f_fumador: document.getElementById('f_fumador'),
  f_limit: document.getElementById('f_limit'),

  // ETL
  etlForm: document.getElementById('etlForm'),
  etlHint: document.getElementById('etlHint'),
  etlRuns: document.getElementById('etlRuns'),

  // Predicciones
  predictForm: document.getElementById('predictForm'),
  predHint: document.getElementById('predHint'),
  predOutput: document.getElementById('predOutput'),

  // Reportes
  statsOutput: document.getElementById('statsOutput'),
  segOutput: document.getElementById('segOutput'),
};

const STORAGE = {
  token: 'ha_access_token',
  predCount: 'ha_pred_realizadas',
  etlCount: 'ha_etls',
};

function setView(viewName) {
  els.views().forEach(v => {
    const name = v.getAttribute('data-view');
    v.style.display = name === viewName ? 'block' : 'none';
  });
}

function setActiveNav(route) {
  document.querySelectorAll('.nav-item').forEach(a => {
    const isActive = a.getAttribute('data-route') === route;
    a.classList.toggle('is-active', isActive);
  });
}

function setCrumb(route) {
  const map = {
    dashboard: 'Dashboard',
    pacientes: 'Pacientes',
    etl: 'ETL',
    predicciones: 'Predicciones',
    reportes: 'Reportes',
    login: 'Iniciar sesión'
  };
  els.crumb.textContent = map[route] || 'Dashboard';
}

function getRoute() {
  const h = location.hash || '#/dashboard';
  const r = h.replace('#/', '');
  const allowed = new Set(['dashboard', 'pacientes', 'etl', 'predicciones', 'reportes']);
  return allowed.has(r) ? r : 'dashboard';
}

async function loadKPIs() {
  const data = await api.getDashboardKpis();
  els.kpi_total.textContent = data.total_records ?? 0;
  els.kpi_critical.textContent = data.critical_patients ?? 0;
  els.kpi_avg_risk.textContent = (typeof data.avg_risk === 'number') ? data.avg_risk.toFixed(2) : (data.avg_risk ?? 0);
  els.kpi_diabetic.textContent = data.diabetic_patients ?? 0;
  els.kpi_hypertensive.textContent = data.hypertensive_patients ?? 0;

  els.kpi_pred_realizadas.textContent = String(+localStorage.getItem(STORAGE.predCount) || 0);
  els.kpi_etls.textContent = String(+localStorage.getItem(STORAGE.etlCount) || 0);

  // Charts from reports/analytics (aprox)
  const seg = await api.getReports();
  const analytics = await api.getAnalyticsStats();

  charts.renderRiskBars(seg);
  charts.renderTrends(seg, analytics);
  charts.renderSexPie(seg);
  charts.renderHeatmap(seg);
}

async function loadPacientes() {
  els.tblPacientes.innerHTML = '';
  els.pacientesMeta.textContent = 'Cargando...';

  const params = new URLSearchParams();
  if (els.f_riesgo.value) params.set('riesgo_enfermedad', els.f_riesgo.value);
  if (els.f_sexo.value) params.set('sexo', els.f_sexo.value);
  if (els.f_fumador.value !== '') params.set('fumador', els.f_fumador.value);
  params.set('limit', els.f_limit.value || '50');

  const resp = await api.getPacientes(params.toString());
  const rows = resp.results || [];
  els.pacientesMeta.textContent = `Mostrando ${rows.length} de ${resp.count}`;

  const frag = document.createDocumentFragment();
  for (const p of rows) {
    const tr = document.createElement('tr');
    const nombre = [p.names, p.last_names].filter(Boolean).join(' ');
    tr.innerHTML = `
      <td>${p.id ?? ''}</td>
      <td>${nombre || ''}</td>
      <td>${p.age ?? ''}</td>
      <td>${p.imc ?? ''}</td>
      <td>${p.glucosa ?? ''}</td>
      <td>${p.presion_sistolica ?? ''}/${p.presion_diastolica ?? ''}</td>
      <td>${p.fumador === null || p.fumador === undefined ? '' : (p.fumador ? 'Sí' : 'No')}</td>
      <td><span class="badge ${charts.riskClass(p.riesgo_enfermedad)}">${p.riesgo_enfermedad ?? ''}</span></td>
    `;
    frag.appendChild(tr);
  }
  els.tblPacientes.appendChild(frag);
}

function localAddEtlRun(run) {
  const prev = JSON.parse(localStorage.getItem('ha_etl_runs') || '[]');
  prev.unshift(run);
  localStorage.setItem('ha_etl_runs', JSON.stringify(prev.slice(0, 8)));
}

function renderEtlRuns() {
  const runs = JSON.parse(localStorage.getItem('ha_etl_runs') || '[]');
  els.etlRuns.innerHTML = '';
  if (!runs.length) {
    els.etlRuns.innerHTML = '<div class="muted">Aún no hay ejecuciones.</div>';
    return;
  }
  for (const r of runs) {
    const div = document.createElement('div');
    div.className = 'list-item';
    div.innerHTML = `
      <div class="li-main">
        <div class="li-title">ETL #${r.index}</div>
        <div class="li-sub">${new Date(r.ts).toLocaleString()}</div>
      </div>
      <div class="li-right">
        <span class="pill">${r.status}</span>
      </div>
    `;
    els.etlRuns.appendChild(div);
  }
}

async function loadReportes() {
  const [seg, stats] = await Promise.all([api.getReports(), api.getAnalyticsStats2()]);
  els.segOutput.textContent = JSON.stringify(seg, null, 2);
  els.statsOutput.textContent = JSON.stringify(stats, null, 2);
}

function requireAuthOrLogin() {
  const token = localStorage.getItem(STORAGE.token);
  const logged = Boolean(token);
  if (!logged) {
    setView('login');
    setCrumb('login');
    els.userPill.textContent = 'No autenticado';
    // logout buttons shouldn't exist without auth
    document.querySelector('.sidebar-footer').style.display = 'none';
    return false;
  }
  document.querySelector('.sidebar-footer').style.display = 'flex';
  els.userPill.textContent = 'Conectado';
  return true;
}

async function bootstrap() {
  // Theme
  const dark = localStorage.getItem('ha_dark') !== 'false';
  document.documentElement.dataset.theme = dark ? 'dark' : 'light';

  els.btnTheme.addEventListener('click', () => {
    const isDark = document.documentElement.dataset.theme === 'dark';
    document.documentElement.dataset.theme = isDark ? 'light' : 'dark';
    localStorage.setItem('ha_dark', isDark ? 'false' : 'true');
  });

  // Logout
  els.btnLogout.addEventListener('click', () => {
    localStorage.removeItem(STORAGE.token);
    api.clearToken();
    location.hash = '#/login';
    setView('login');
    setCrumb('login');
    els.userPill.textContent = 'No autenticado';
  });

  // Login
  els.loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    els.loginHint.textContent = 'Validando...';

    const form = new FormData(els.loginForm);
    const payload = { username: form.get('username'), password: form.get('password') };
    try {
      const r = await api.login(payload);
      localStorage.setItem(STORAGE.token, r.access);
      api.setToken(r.access);
      els.loginHint.textContent = 'Login OK';
      localStorage.setItem(STORAGE.predCount, localStorage.getItem(STORAGE.predCount) || '0');
      localStorage.setItem(STORAGE.etlCount, localStorage.getItem(STORAGE.etlCount) || '0');

      // go dashboard
      location.hash = '#/dashboard';
      const ok = requireAuthOrLogin();
      if (ok) {
        els.views().forEach(v => v.style.display = 'none');
        // route loader will show view
      }
    } catch (err) {
      els.loginHint.textContent = err?.detail || err?.message || 'Error de login';
    }
  });

  // Navigation router
  window.addEventListener('hashchange', async () => {
    const tokenOk = requireAuthOrLogin();
    const route = getRoute();
    if (!tokenOk) return;

    setActiveNav(route);
    setCrumb(route);
    setView(route);

    if (route === 'dashboard') await loadKPIs();
    if (route === 'pacientes') await loadPacientes();
    if (route === 'etl') {
      renderEtlRuns();
    }
    if (route === 'reportes') await loadReportes();
  });

  // Pacientes
  els.btnLoadPacientes.addEventListener('click', () => loadPacientes());

  // ETL
  els.etlForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    els.etlHint.textContent = 'Ejecutando ETL...';

    const form = new FormData(els.etlForm);
    const file = form.get('file');

    try {
      const resp = await api.runEtl(file || null);

      const predCount = +localStorage.getItem(STORAGE.predCount) || 0;
      const etlCount = (+localStorage.getItem(STORAGE.etlCount) || 0) + 1;
      localStorage.setItem(STORAGE.etlCount, String(etlCount));

      const idx = etlCount;
      localAddEtlRun({ index: idx, ts: Date.now(), status: 'SUCCESS', payload: resp });
      renderEtlRuns();
      els.etlHint.textContent = `ETL OK. Loaded: ${resp.records_loaded ?? '—'}`;

      // refresh KPIs if on dashboard
      if (getRoute() === 'dashboard') await loadKPIs();
    } catch (err) {
      const idx = (+localStorage.getItem(STORAGE.etlCount) || 0) + 1;
      localAddEtlRun({ index: idx, ts: Date.now(), status: 'FAILED', payload: err });
      renderEtlRuns();
      els.etlHint.textContent = err?.detail || err?.message || 'Error ETL';
    }
  });

  // Predicciones
  els.predictForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    els.predHint.textContent = 'Ejecutando...';
    els.predOutput.textContent = '—';

    const form = new FormData(els.predictForm);
    const values = Object.fromEntries(form.entries());

    const hasAny = Object.values(values).some(v => v !== null && String(v).trim() !== '');
    const inputs = [];

    if (hasAny) {
      const fumador = String(values.fumador || '').toLowerCase();
      const fumadorBool = (fumador === 'true' || fumador === '1' || fumador === 'si' || fumador === 'sí');

      inputs.push({
        imc: values.imc !== '' ? Number(values.imc) : undefined,
        age: values.age !== '' ? Number(values.age) : undefined,
        glucosa: values.glucosa !== '' ? Number(values.glucosa) : undefined,
        colesterol: values.colesterol !== '' ? Number(values.colesterol) : undefined,
        presion_sistolica: values.presion_sistolica !== '' ? Number(values.presion_sistolica) : undefined,
        frecuencia_cardiaca: values.frecuencia_cardiaca !== '' ? Number(values.frecuencia_cardiaca) : undefined,
        fumador: fumadorBool,
      });

      // remove undefined keys
      const clean = inputs[0];
      Object.keys(clean).forEach(k => clean[k] === undefined && delete clean[k]);
      inputs[0] = clean;
    }

    try {
      const resp = await api.predict({ inputs: hasAny ? inputs : [] });
      els.predHint.textContent = 'OK';
      els.predOutput.textContent = JSON.stringify(resp, null, 2);

      const next = (+localStorage.getItem(STORAGE.predCount) || 0) + 1;
      localStorage.setItem(STORAGE.predCount, String(next));
      // refresh KPIs
      if (getRoute() === 'dashboard') await loadKPIs();
    } catch (err) {
      els.predHint.textContent = err?.detail || err?.message || 'Error predicciones';
      els.predOutput.textContent = JSON.stringify(err, null, 2);
    }
  });

  // Initial boot
  const tokenOk = requireAuthOrLogin();
  const route = getRoute();
  if (tokenOk) {
    document.querySelector('.sidebar-footer').style.display = 'flex';
    setActiveNav(route);
    setCrumb(route);
    setView(route);
    renderEtlRuns();
    if (route === 'dashboard') await loadKPIs();
    if (route === 'pacientes') await loadPacientes();
    if (route === 'reportes') await loadReportes();
  } else {
    setView('login');
    setCrumb('login');
  }
}

bootstrap();

