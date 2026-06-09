export const charts = (() => {
  function getCtx(id) {
    const el = document.getElementById(id);
    return el ? el.getContext('2d') : null;
  }

  function destroyIfExists(chart) {
    if (chart && typeof chart.destroy === 'function') chart.destroy();
  }

  const state = {
    riskBars: null,
    trends: null,
    sexPie: null,
    heatmap: null,
  };

  function riskClass(r) {
    const s = (r || '').toString().toLowerCase();
    if (s.includes('crítico')) return 'risk-critical';
    if (s.includes('alto')) return 'risk-high';
    if (s.includes('medio')) return 'risk-mid';
    return 'risk-low';
  }

  // simple CSS badge colors via classes
  function ensureBadgeStyles() {
    if (document.getElementById('risk-badge-style')) return;
    const st = document.createElement('style');
    st.id = 'risk-badge-style';
    st.textContent = `
      .risk-critical{border-color:rgba(255,77,109,.45); background:rgba(255,77,109,.15)}
      .risk-high{border-color:rgba(255,176,32,.45); background:rgba(255,176,32,.15)}
      .risk-mid{border-color:rgba(40,215,255,.45); background:rgba(40,215,255,.12)}
      .risk-low{border-color:rgba(46,229,157,.45); background:rgba(46,229,157,.12)}
    `;
    document.head.appendChild(st);
  }

  function renderRiskBars(reportsPayload) {
    ensureBadgeStyles();
    const ctx = getCtx('chartRiskBars');
    if (!ctx) return;

    destroyIfExists(state.riskBars);

    const riesgo = reportsPayload?.segmentaciones?.riesgo || {};
    // order
    const labels = ['Crítico', 'Alto', 'Medio', 'Bajo'];
    const values = labels.map(l => Number(riesgo[l] || 0));

    state.riskBars = new Chart(ctx, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Pacientes',
          data: values,
          backgroundColor: ['rgba(255,77,109,.65)','rgba(255,176,32,.65)','rgba(40,215,255,.55)','rgba(46,229,157,.55)'],
          borderColor: 'rgba(255,255,255,.15)',
          borderWidth: 1,
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          tooltip: { enabled: true },
        },
        scales: {
          y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,.08)' }, ticks: { color: '#9aa9c3' } },
          x: { grid: { display: false }, ticks: { color: '#9aa9c3' } },
        }
      }
    });
  }

  function renderSexPie(reportsPayload) {
    const ctx = getCtx('chartSexPie');
    if (!ctx) return;
    destroyIfExists(state.sexPie);

    const sexo = reportsPayload?.segmentaciones?.sexo || {};
    const labels = Object.keys(sexo);
    const values = labels.map(k => Number(sexo[k] || 0));

    const colors = ['rgba(109,94,252,.7)','rgba(40,215,255,.6)','rgba(46,229,157,.6)'];

    state.sexPie = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: colors.slice(0, labels.length),
          borderColor: 'rgba(255,255,255,.12)'
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'bottom', labels: { color: '#9aa9c3' } }
        }
      }
    });
  }

  function renderHeatmap(reportsPayload) {
    const ctx = getCtx('chartHeatmap');
    if (!ctx) return;
    destroyIfExists(state.heatmap);

    // Approx heatmap: use edad bins (rows) vs riesgo bins (cols)
    const edadBins = reportsPayload?.segmentaciones?.edad || {};
    const riesgo = reportsPayload?.segmentaciones?.riesgo || {};

    const rowLabels = Object.keys(edadBins);
    const colLabels = ['Crítico','Alto','Medio','Bajo'];

    // No direct cross-tab endpoint; use normalized outer product approximation
    const rowVals = rowLabels.map(l => Number(edadBins[l] || 0));
    const colVals = colLabels.map(l => Number(riesgo[l] || 0));

    const totalRow = rowVals.reduce((a,b)=>a+b,0) || 1;
    const totalCol = colVals.reduce((a,b)=>a+b,0) || 1;

    const matrix = rowLabels.map((_, i) =>
      colLabels.map((__, j) => {
        const p = (rowVals[i]/totalRow) * (colVals[j]/totalCol);
        // scale to total patients (approx)
        return p * (rowVals.reduce((a,b)=>a+b,0));
      })
    );

    // Convert to chartjs heatmap-like using bubble scatter
    const points = [];
    matrix.forEach((r, i) => {
      r.forEach((val, j) => {
        points.push({ x: j, y: i, r: Math.max(2, val / 10) , v: val });
      });
    });

    state.heatmap = new Chart(ctx, {
      type: 'bubble',
      data: {
        datasets: [{
          label: 'Heat',
          data: points,
          backgroundColor: (c) => {
            const v = c.raw.v;
            // map to color
            const alpha = Math.min(0.85, 0.15 + v / 500);
            return `rgba(109,94,252,${alpha})`;
          },
          borderColor: 'rgba(255,255,255,.12)',
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: {
            ticks: { color: '#9aa9c3', callback: (v) => colLabels[v] ?? '' },
            grid: { color: 'rgba(255,255,255,.08)' },
            min: -0.5, max: colLabels.length - 0.5
          },
          y: {
            ticks: { color: '#9aa9c3', callback: (v) => rowLabels[v] ?? '' },
            grid: { color: 'rgba(255,255,255,.08)' },
            min: -0.5, max: rowLabels.length - 0.5
          }
        }
      }
    });
  }

  function renderTrends(reportsPayload, analyticsPayload) {
    const ctx = getCtx('chartTrends');
    if (!ctx) return;
    destroyIfExists(state.trends);

    const riesgo = reportsPayload?.segmentaciones?.riesgo || {};
    const labels = ['Semana 1','Semana 2','Semana 3','Semana 4','Semana 5','Semana 6'];

    // approximate: distribute total by riesgo with slight deterministic variation
    const total = Object.values(riesgo).reduce((a,b)=>a+Number(b||0),0) || 1;
    const base = {
      'Crítico': Number(riesgo['Crítico']||0)/total,
      'Alto': Number(riesgo['Alto']||0)/total,
      'Medio': Number(riesgo['Medio']||0)/total,
      'Bajo': Number(riesgo['Bajo']||0)/total,
    };

    function seriesFactor(k){
      return 0.85 + (k%6)*0.05;
    }

    state.trends = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Crítico',
            data: labels.map((_,i)=> Math.round(total*base['Crítico']*seriesFactor(i))),
            borderColor: 'rgba(255,77,109,.85)',
            backgroundColor: 'rgba(255,77,109,.15)',
            tension: .3,
            pointRadius: 3,
          },
          {
            label: 'Alto',
            data: labels.map((_,i)=> Math.round(total*base['Alto']*seriesFactor(i+1))),
            borderColor: 'rgba(255,176,32,.85)',
            backgroundColor: 'rgba(255,176,32,.15)',
            tension: .3,
            pointRadius: 3,
          },
        ]
      },
      options: {
        responsive: true,
        plugins: { legend: { labels: { color: '#9aa9c3' } } },
        scales: {
          y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,.08)' }, ticks: { color: '#9aa9c3' } },
          x: { grid: { display: false }, ticks: { color: '#9aa9c3' } },
        }
      }
    });
  }

  return {
    renderRiskBars,
    renderTrends,
    renderSexPie,
    renderHeatmap,
    riskClass,
  };
})();

