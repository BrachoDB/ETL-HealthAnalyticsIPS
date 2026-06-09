async function refreshKpis() {
  const loading = document.getElementById('kpis-loading');
  if (loading) loading.setAttribute('aria-busy', 'true');

  const kCritical = document.getElementById('kpi-critical');
  const kHypert = document.getElementById('kpi-hypertensive');
  const kDiab = document.getElementById('kpi-diabetic');
  const kSmoker = document.getElementById('kpi-smoker');
  const kAvg = document.getElementById('kpi-avg-risk');

  try {
    const data = await window.api.apiFetch('/api/dashboard/dashboard/kpis/', { method: 'GET' });
    if (kCritical) kCritical.textContent = String(data.critical_patients ?? '-');
    if (kHypert) kHypert.textContent = String(data.hypertensive_patients ?? '-');
    if (kDiab) kDiab.textContent = String(data.diabetic_patients ?? '-');
    if (kSmoker) kSmoker.textContent = String(data.smoker_patients ?? '-');
    if (kAvg) kAvg.textContent = String(data.avg_risk ?? '-');
  } catch (e) {
    if (kCritical) kCritical.textContent = '—';
  } finally {
    if (loading) loading.setAttribute('aria-busy', 'false');
  }
}

async function refreshReportes() {
  const statsEl = document.getElementById('reportes-stats');
  const segEl = document.getElementById('reportes-seg');

  try {
    const data = await window.api.apiFetch('/api/reports/reportes/', { method: 'GET' });

    if (statsEl) {
      const s = data.stats || {};
      statsEl.innerHTML = `\n        <div>IMC: media ${s.imc?.media ?? 0} / mediana ${s.imc?.mediana ?? 0} / moda ${s.imc?.moda ?? '-'}</div>\n        <div>Edad: media ${s.edad?.media ?? 0} / mediana ${s.edad?.mediana ?? 0} / moda ${s.edad?.moda ?? '-'}</div>\n        <div>Glucosa: media ${s.glucosa?.media ?? 0} / mediana ${s.glucosa?.mediana ?? 0} / moda ${s.glucosa?.moda ?? '-'}</div>\n      `;
    }

    if (segEl) segEl.textContent = 'Segmentaciones listas';

    if (window.charts) {
      const imc = data.segmentaciones?.imc || {};
      const edad = data.segmentaciones?.edad || {};

      const imcLabels = Object.keys(imc);
      const imcValues = imcLabels.map(k => imc[k]);
      const ageLabels = Object.keys(edad);
      const ageValues = ageLabels.map(k => edad[k]);

      window.charts.drawBars('chart-imc-2', imcLabels, imcValues);
      window.charts.drawBars('chart-age-2', ageLabels, ageValues);
    }
  } catch (e) {
    if (statsEl) statsEl.textContent = 'Error al cargar';
    if (segEl) segEl.textContent = '—';
  }
}

async function loadPacientes() {
  const tbody = document.getElementById('pacientes-tbody');
  const meta = document.getElementById('pacientes-meta');
  const empty = document.getElementById('pacientes-empty');

  if (!tbody) return;

  const riesgo = document.getElementById('filter-riesgo')?.value || '';
  const sexo = document.getElementById('filter-sexo')?.value || '';
  const fumador = document.getElementById('filter-fumador')?.value || '';
  const limit = document.getElementById('filter-limit')?.value || '50';

  const params = new URLSearchParams();
  if (riesgo) params.set('riesgo_enfermedad', riesgo);
  if (sexo) {
    // el backend filtra por sex__iexact, mapear masculino/femenino a valores esperados
    // como dataset usa 'Masculino'/'Femenino' se mantiene
    params.set('sexo', sexo);
  }
  if (fumador) params.set('fumador', fumador);
  params.set('limit', limit);

  try {
    empty && (empty.style.display = 'none');
    tbody.innerHTML = '';

    const data = await window.api.apiFetch('/api/etl/pacientes/?' + params.toString(), { method: 'GET' });
    const results = data.results || [];

    meta && (meta.textContent = `Total: ${data.count ?? results.length} • Mostrando: ${results.length}`);

    if (!results.length) {
      empty && (empty.style.display = 'block');
      return;
    }

    results.forEach(p => {
      const tr = document.createElement('tr');
      const presion = [p.presion_sistolica, p.presion_diastolica].filter(Boolean).join('/') || '—';
      tr.innerHTML = `
        <td>${p.id ?? ''}</td>
        <td>${(p.names ? p.names : '')} ${(p.last_names ? p.last_names : '')}</td>
        <td>${p.age ?? '—'}</td>
        <td>${p.sex ?? '—'}</td>
        <td>${p.imc ?? '—'}</td>
        <td>${p.glucosa ?? '—'}</td>
        <td>${presion}</td>
        <td>${p.fumador === true ? 'Sí' : p.fumador === false ? 'No' : '—'}</td>
        <td>${p.riesgo_enfermedad ?? '—'}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (e) {
    meta && (meta.textContent = 'Error');
  }
}

async function runPredicciones() {
  const btn = document.getElementById('btn-run-pred');
  if (!btn) return;

  btn.addEventListener('click', async () => {
    const err = document.getElementById('pred-error');
    const metricsEl = document.getElementById('pred-metrics');
    const resultsEl = document.getElementById('pred-results');

    const payload = {
      inputs: [
        {
          imc: Number(document.getElementById('in-imc')?.value ?? 0),
          age: Number(document.getElementById('in-edad')?.value ?? 0),
          glucosa: Number(document.getElementById('in-glucosa')?.value ?? 0),
          colesterol: Number(document.getElementById('in-colesterol')?.value ?? 0),
          presion_sistolica: Number(document.getElementById('in-ps')?.value ?? 0),
          frecuencia_cardiaca: Number(document.getElementById('in-fc')?.value ?? 0),
          fumador: document.getElementById('in-fumador')?.value === 'true'
        }
      ]
    };

    err && (err.style.display = 'none');
    if (metricsEl) metricsEl.textContent = 'Cargando…';
    if (resultsEl) resultsEl.textContent = '';

    try {
      const data = await window.api.apiFetch('/api/ml/predicciones/', { method: 'POST', body: payload });
      if (metricsEl) {
        const m = data.metrics || {};
        metricsEl.innerHTML = `\n          <div>Accuracy: ${m.accuracy ?? '—'}</div>\n          <div>Precision: ${m.precision ?? '—'}</div>\n          <div>Recall: ${m.recall ?? '—'}</div>\n          <div>F1: ${m.f1_score ?? '—'}</div>\n        `;
      }

      if (data.predictions && resultsEl) {
        const preds = data.predictions;
        resultsEl.innerHTML = preds.map(p => `<div><b>${p.riesgo_predicho}</b></div>`).join('');
      }
    } catch (e) {
      if (err) {
        err.textContent = String(e.message || e);
        err.style.display = 'block';
      }
    }
  });
}

// init
(function init() {
  if (window.__DASHBOARD__ && window.__DASHBOARD__.kpisLoading) {
    refreshKpis();
    const btn = document.getElementById('btn-refresh');
    if (btn) btn.addEventListener('click', refreshKpis);
  }

  if (window.__REPORTES__) {
    refreshReportes();
    const btn = document.getElementById('btn-load-reportes');
    btn && btn.addEventListener('click', refreshReportes);
  }

  if (window.__PACIENTES__) {
    loadPacientes();
    const btn = document.getElementById('btn-load');
    btn && btn.addEventListener('click', loadPacientes);
  }

  runPredicciones();
})();

window.dashboard = { refreshKpis, refreshReportes, loadPacientes };

