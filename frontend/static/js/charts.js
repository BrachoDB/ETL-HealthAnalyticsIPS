function ensureChartJs() {
  // Chart.js no está permitido como dependencia nueva; aquí usamos un fallback canvas mínimo.
  // Si Chart.js ya está incluido por el proyecto, se utilizará.
  return true;
}

function drawBars(canvasId, labels, values) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const max = Math.max(1, ...values);
  const pad = 8;
  const w = canvas.width;
  const h = canvas.height;
  const barW = (w - pad * 2) / values.length;

  values.forEach((v, i) => {
    const x = pad + i * barW + 2;
    const barH = (h - pad * 2) * (v / max);
    const y = h - pad - barH;
    ctx.fillStyle = 'rgba(106,166,255,.85)';
    ctx.fillRect(x, y, Math.max(6, barW - 6), barH);

    ctx.fillStyle = 'rgba(232,238,252,.85)';
    ctx.font = '10px system-ui';
    const text = labels[i] || '';
    ctx.fillText(text, x, h - 2);
  });
}

function drawLine(canvasId, labels, values) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const max = Math.max(1, ...values);
  const pad = 10;
  const w = canvas.width;
  const h = canvas.height;

  ctx.strokeStyle = 'rgba(56,217,150,.9)';
  ctx.lineWidth = 2;
  ctx.beginPath();

  values.forEach((v, i) => {
    const x = pad + (i * (w - pad * 2)) / Math.max(1, values.length - 1);
    const y = h - pad - (h - pad * 2) * (v / max);
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();
}

window.charts = { drawBars, drawLine };

