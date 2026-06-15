window.riskColors = {
    'Bajo': '#28a745',
    'Medio': '#ffc107',
    'Alto': '#fd7e14',
    'Crítico': '#dc3545'
};

function loadRiskChart(distribution) {
    if (typeof Chart === 'undefined') {
        return;
    }

    const canvas = document.getElementById('chartRiesgo');
    if (!canvas) {
        return;
    }

    const labels = distribution.map(item => item.riesgo_enfermedad);
    const counts = distribution.map(item => item.count);

    new Chart(canvas.getContext('2d'), {
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

    const datasets = ageRisk.datasets.map(dataset => ({
        ...dataset,
        backgroundColor: window.riskColors[dataset.label] || '#6c757d'
    }));

    new Chart(canvas.getContext('2d'), {
        type: 'bar',
        data: {
            labels: ageRisk.labels,
            datasets: datasets
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

    new Chart(canvas.getContext('2d'), {
        type: 'bar',
        data: {
            labels: diagnosticos.labels,
            datasets: [{
                label: 'Pacientes',
                data: diagnosticos.data,
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

    new Chart(canvas.getContext('2d'), {
        type: 'line',
        data: {
            labels: mensual.labels,
            datasets: mensual.datasets
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

    new Chart(canvas.getContext('2d'), {
        type: 'line',
        data: {
            labels: trends.labels,
            datasets: trends.datasets
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
