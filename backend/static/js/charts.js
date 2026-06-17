window.riskColors = {
    'Bajo': '#28a745',
    'Medio': '#ffc107',
    'Alto': '#fd7e14',
    'Crítico': '#dc3545'
};

function getArray(value) {
    return Array.isArray(value) ? value : [];
}

function showChartEmptyState(canvas, message) {
    canvas.style.display = 'none';
    const parent = canvas.parentElement;
    const placeholder = parent.querySelector('.chart-empty-state');
    if (!placeholder) {
        const element = document.createElement('div');
        element.className = 'alert alert-info mb-0 chart-empty-state';
        parent.appendChild(element);
    }
    parent.querySelector('.chart-empty-state').textContent = message;
}

function hideChartEmptyState(canvas) {
    canvas.style.display = '';
    canvas.parentElement.querySelectorAll('.chart-empty-state').forEach(element => element.remove());
}

function destroyChart(canvas) {
    if (canvas?.chart) {
        canvas.chart.destroy();
        canvas.chart = null;
    }
}

function createChart(canvas, config) {
    destroyChart(canvas);
    hideChartEmptyState(canvas);
    const chart = new Chart(canvas.getContext('2d'), config);
    canvas.chart = chart;
    return chart;
}

function loadRiskChart(distribution) {
    if (typeof Chart === 'undefined') {
        return;
    }

    const canvas = document.getElementById('chartRiesgo');
    if (!canvas) {
        return;
    }

    const rows = getArray(distribution);
    if (!rows.length) {
        showChartEmptyState(canvas, 'No hay datos de riesgo para mostrar');
        return;
    }

    const labels = rows.map(item => item.riesgo_enfermedad || 'Sin dato');
    const counts = rows.map(item => item.count || 0);

    createChart(canvas, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: counts,
                backgroundColor: labels.map(label => window.riskColors[label] || '#6c757d')
            }]
        }
    });
}

function loadAgeRiskChart(ageRisk) {
    if (typeof Chart === 'undefined') {
        return;
    }

    const canvas = document.getElementById('chartEdadRiesgo');
    if (!canvas) {
        return;
    }

    const labels = getArray(ageRisk?.labels);
    const datasets = getArray(ageRisk?.datasets);
    if (!labels.length || !datasets.length) {
        showChartEmptyState(canvas, 'No hay datos de edad y riesgo para mostrar');
        return;
    }

    createChart(canvas, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets.map(dataset => ({
                ...dataset,
                data: getArray(dataset.data),
                backgroundColor: window.riskColors[dataset.label] || '#6c757d'
            }))
        },
        options: {
            responsive: true,
            scales: {
                x: { stacked: true },
                y: { stacked: true, beginAtZero: true }
            }
        }
    });
}

function loadDiagnosticoChart(diagnosticos) {
    if (typeof Chart === 'undefined') {
        return;
    }

    const canvas = document.getElementById('chartDiagnosticos');
    if (!canvas) {
        return;
    }

    const labels = getArray(diagnosticos?.labels);
    const data = getArray(diagnosticos?.data);
    if (!labels.length || !data.length) {
        showChartEmptyState(canvas, 'No hay datos de diagnósticos para mostrar');
        return;
    }

    createChart(canvas, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Pacientes',
                data: data,
                backgroundColor: '#0dcaf0'
            }]
        },
        options: {
            responsive: true,
            indexAxis: 'y'
        }
    });
}

function loadMensualChart(mensual) {
    if (typeof Chart === 'undefined') {
        return;
    }

    const canvas = document.getElementById('chartMensual');
    if (!canvas) {
        return;
    }

    const labels = getArray(mensual?.labels);
    const datasets = getArray(mensual?.datasets);
    if (!labels.length || !datasets.length) {
        showChartEmptyState(canvas, 'No hay datos mensuales para mostrar');
        return;
    }

    createChart(canvas, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true },
                y1: { beginAtZero: true, position: 'right', grid: { drawOnChartArea: false } }
            }
        }
    });
}

function loadTrendChart(trends) {
    if (typeof Chart === 'undefined') {
        return;
    }

    const canvas = document.getElementById('chartTendencias');
    if (!canvas) {
        return;
    }

    const labels = getArray(trends?.labels);
    const datasets = getArray(trends?.datasets);
    if (!labels.length || !datasets.length) {
        showChartEmptyState(canvas, 'No hay datos de tendencias para mostrar');
        return;
    }

    createChart(canvas, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true },
                y1: { beginAtZero: true, position: 'right', grid: { drawOnChartArea: false } }
            }
        }
    });
}

function loadEdadesChart(pacientes) {
    if (typeof Chart === 'undefined') {
        return;
    }

    const canvas = document.getElementById('chartEdades');
    if (!canvas) {
        return;
    }

    const rows = getArray(pacientes);
    if (!rows.length) {
        showChartEmptyState(canvas, 'No hay pacientes para mostrar');
        return;
    }

    hideChartEmptyState(canvas);

    const groups = {
        '0-17': 0,
        '18-29': 0,
        '30-44': 0,
        '45-59': 0,
        '60-74': 0,
        '75+': 0,
    };

    rows.forEach(paciente => {
        const edad = Number.parseInt(paciente.edad, 10);
        if (Number.isNaN(edad)) {
            return;
        }

        if (edad < 18) {
            groups['0-17'] += 1;
        } else if (edad < 30) {
            groups['18-29'] += 1;
        } else if (edad < 45) {
            groups['30-44'] += 1;
        } else if (edad < 60) {
            groups['45-59'] += 1;
        } else if (edad < 75) {
            groups['60-74'] += 1;
        } else {
            groups['75+'] += 1;
        }
    });

    createChart(canvas, {
        type: 'bar',
        data: {
            labels: Object.keys(groups),
            datasets: [{
                label: 'Pacientes',
                data: Object.values(groups),
                backgroundColor: '#0d6efd',
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1 } }
            }
        }
    });
}
