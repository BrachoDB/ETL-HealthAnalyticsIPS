(function () {
    const api = window.HealthAnalyticsAPI;
    const isDashboard = Boolean(document.getElementById('dashboardPage'));
    const isAnalytics = Boolean(document.getElementById('analyticsPage'));
    const isPacientes = Boolean(document.getElementById('pacientesPage'));
    const shouldLoadAnalytics = isDashboard || isAnalytics;
    let pacientesRecientes = [];
    let activeRiskFilter = 'todos';

    function escapeHTML(value) {
        if (value === null || value === undefined) {
            return '';
        }

        return String(value)
            .replaceAll('&', '&amp;')
            .replaceAll('<', '&lt;')
            .replaceAll('>', '&gt;')
            .replaceAll('"', '&quot;')
            .replaceAll("'", '&#039;');
    }

    function formatNumber(value, digits = 2) {
        const number = Number.parseFloat(value);
        if (Number.isNaN(number)) {
            return '0';
        }
        return number.toFixed(digits);
    }

    function formatDate(value) {
        if (!value) {
            return '';
        }

        const date = new Date(value);
        if (Number.isNaN(date.getTime())) {
            return escapeHTML(value);
        }

        return date.toLocaleString();
    }

    function setText(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    function formatLogDetails(details) {
        const text = String(details || '').replace(/\s+/g, ' ').trim();
        if (!text) {
            return '<span class="text-muted">Sin detalles</span>';
        }

        const truncated = text.length > 160 ? `${text.slice(0, 160)}...` : text;
        return `<span title="${escapeHTML(text)}">${escapeHTML(truncated)}</span>`;
    }

    function showError(message) {
        alert(message);
    }

    function formatApiError(error, fallback) {
        const status = error.response?.status ? `${error.response.status} ` : '';
        const detail = error.response?.data?.detail || error.response?.data?.error || error.message;
        return `${fallback} (${status}${detail || 'sin detalles del servidor'})`;
    }

    function safeLoad(label, loader) {
        try {
            loader();
        } catch (error) {
            console.error(`Error cargando ${label}`, error);
        }
    }

    function redirectLogin() {
        api.clearAuth();
        window.location.href = '/login/';
    }

    async function loadData() {
        try {
            const response = await api.get('/api/analytics/kpis/');
            const data = response.data;

            setText('kpiTotal', data.total_pacientes);
            setText('kpiCriticos', data.pacientes_criticos);
            setText('kpiHipertensos', data.hipertensos);
            setText('kpiImc', formatNumber(data.imc_promedio));

            loadRiskChart(data.riesgo_distribucion);
            loadAgeRiskChart(data.edad_riesgo);
            await loadDashboardExtras();
            if (isDashboard) {
                await loadLogs();
            }
        } catch (error) {
            console.error(error);
            if (api.isAuthError(error)) {
                redirectLogin();
                return;
            }
            showError('No fue posible cargar los indicadores del dashboard.');
        }
    }

    async function loadDashboardExtras() {
        let data;
        try {
            const response = await api.get('/api/analytics/dashboard-extras/');
            data = response.data;
        } catch (error) {
            console.error(error);
            if (api.isAuthError(error)) {
                redirectLogin();
                return;
            }
            showError(formatApiError(error, 'No fue posible cargar los datos analíticos adicionales'));
            return;
        }

        safeLoad('tendencias', () => loadTrendChart(data.tendencias));
        safeLoad('heatmap', () => loadHeatmap(data.heatmap));
        safeLoad('diagnósticos', () => loadDiagnosticoChart(data.diagnosticos));
        safeLoad('mensual', () => loadMensualChart(data.mensual));
        safeLoad('estadística descriptiva', () => loadEstadisticaDescriptiva(data.estadistica));
        safeLoad('pacientes', () => loadPacientes(data.pacientes));
        safeLoad('distribución de edades', () => loadEdadesChart(data.pacientes));
        safeLoad('alertas críticas', () => loadCriticalAlerts(data.criticos));
        safeLoad('segmentación', () => loadSegmentation(data.segmentacion));
        safeLoad('métricas ML', () => loadMLMetrics(data.ml_metricas));
    }

    function loadEstadisticaDescriptiva(estadistica) {
        const container = document.getElementById('estadisticaDescriptiva');
        if (!container) {
            return;
        }

        container.innerHTML = `
            <table class="table table-sm mb-0">
                <thead>
                    <tr>
                        <th>Variable</th>
                        <th>Media</th>
                        <th>Mediana</th>
                        <th>Moda</th>
                        <th>Desv.</th>
                        <th>Mín</th>
                        <th>Máx</th>
                    </tr>
                </thead>
                <tbody>
                    ${estadistica.map(row => `
                        <tr>
                            <td>${escapeHTML(row.variable)}</td>
                            <td>${escapeHTML(row.media)}</td>
                            <td>${escapeHTML(row.mediana)}</td>
                            <td>${escapeHTML(row.moda)}</td>
                            <td>${escapeHTML(row.desviacion)}</td>
                            <td>${escapeHTML(row.min)}</td>
                            <td>${escapeHTML(row.max)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    function loadPacientes(pacientes) {
        pacientesRecientes = pacientes || [];
        renderPacientes(pacientesRecientes);
    }

    function renderPacientes(pacientes) {
        const filterElement = document.getElementById('filtroPacientes');
        const query = filterElement ? filterElement.value.toLowerCase() : '';
        const filtered = (pacientes || []).filter(paciente => {
            const text = `${paciente.nombres} ${paciente.apellidos} ${paciente.diagnostico_preliminar} ${paciente.riesgo_enfermedad}`.toLowerCase();
            const matchesRisk = activeRiskFilter === 'todos' || paciente.riesgo_enfermedad === activeRiskFilter;
            return matchesRisk && text.includes(query);
        });

        const container = document.getElementById('tablaPacientes');
        if (!container) {
            return;
        }

        if (!filtered.length) {
            container.innerHTML = '<div class="alert alert-info mb-0">No hay pacientes para mostrar</div>';
            return;
        }

        container.innerHTML = `
            <table class="table table-sm mb-0">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Paciente</th>
                        <th>Edad</th>
                        <th>Sexo</th>
                        <th>Diagnóstico</th>
                        <th>Riesgo</th>
                        <th>PAS</th>
                        <th>Glucosa</th>
                        <th>Sat. O2</th>
                        <th>Fecha</th>
                    </tr>
                </thead>
                <tbody>
                    ${filtered.map(paciente => `
                        <tr>
                            <td>${escapeHTML(paciente.id_paciente)}</td>
                            <td>${escapeHTML(paciente.nombres)} ${escapeHTML(paciente.apellidos)}</td>
                            <td>${escapeHTML(paciente.edad)}</td>
                            <td>${escapeHTML(paciente.sexo)}</td>
                            <td>${escapeHTML(paciente.diagnostico_preliminar)}</td>
                            <td><span class="risk-badge" style="background:${window.riskColors[paciente.riesgo_enfermedad] || '#6c757d'}">${escapeHTML(paciente.riesgo_enfermedad)}</span></td>
                            <td>${escapeHTML(paciente.presion_sistolica)}</td>
                            <td>${escapeHTML(paciente.glucosa)}</td>
                            <td>${escapeHTML(paciente.saturacion_oxigeno)}</td>
                            <td>${escapeHTML(paciente.fecha_consulta)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    function loadHeatmap(heatmap) {
        const container = document.getElementById('heatmapEdadRiesgo');
        if (!container || !heatmap) {
            return;
        }

        const maxValue = Math.max(...heatmap.matrix.flat(), 1);
        const header = `<div class="row g-1 mb-1"><div class="col-4 fw-bold">Edad</div>${heatmap.risks.map(risk => `<div class="col-2 text-center fw-bold">${escapeHTML(risk)}</div>`).join('')}</div>`;
        const rows = heatmap.labels.map(label => {
            const index = heatmap.labels.indexOf(label);
            const values = heatmap.matrix[index] || [];
            const cells = values.map(value => {
                const intensity = Math.min(1, value / maxValue);
                const color = `rgba(220, 53, 69, ${0.15 + intensity * 0.75})`;
                return `<div class="col-2 text-center border rounded py-1 heatmap-cell" style="background:${color}">${escapeHTML(value)}</div>`;
            }).join('');
            return `<div class="row g-1 mb-1"><div class="col-4">${escapeHTML(label)}</div>${cells}</div>`;
        }).join('');

        container.innerHTML = header + rows;
    }

    function loadCriticalAlerts(criticos) {
        const list = document.getElementById('listaCriticos');
        if (!list) {
            return;
        }

        const alerts = criticos || [];
        if (!alerts.length) {
            list.innerHTML = '<li class="list-group-item text-success">No hay alertas críticas activas</li>';
            return;
        }

        list.innerHTML = alerts.map(paciente => `
            <li class="list-group-item">
                <strong>${escapeHTML(paciente.nombres)} ${escapeHTML(paciente.apellidos)}</strong> - ${escapeHTML(paciente.riesgo_enfermedad)}<br>
                <span class="text-danger">PA ${escapeHTML(paciente.presion_sistolica)}</span> |
                Glucosa ${escapeHTML(paciente.glucosa)} |
                Sat. O2 ${escapeHTML(paciente.saturacion_oxigeno)}
            </li>
        `).join('');
    }

    function loadSegmentation(segmentacion) {
        const container = document.getElementById('segmentacionPacientes');
        if (!container || !segmentacion) {
            return;
        }

        const sections = [
            { title: 'Por sexo', rows: segmentacion.sexo || [] },
            { title: 'Por riesgo', rows: segmentacion.riesgo || [] },
            { title: 'Por diagnóstico', rows: segmentacion.diagnostico || [] },
        ];

        container.innerHTML = sections.map(section => `
            <div class="card mb-3">
                <div class="card-header">${escapeHTML(section.title)}</div>
                <div class="card-body p-0">
                    <table class="table table-sm mb-0">
                        <thead>
                            <tr>
                                <th>Categoría</th>
                                <th>Total</th>
                                <th>Críticos</th>
                                <th>IMC promedio</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${section.rows.map(row => `
                                <tr>
                                    <td>${escapeHTML(row.label)}</td>
                                    <td>${escapeHTML(row.total)}</td>
                                    <td>${escapeHTML(row.criticos)}</td>
                                    <td>${escapeHTML(row.imc_promedio)}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `).join('');
    }

    function loadMLMetrics(metricas) {
        const container = document.getElementById('mlMetricas');
        if (!container) {
            return;
        }

        if (!metricas) {
            container.innerHTML = 'No hay métricas registradas. Ejecute <strong>train_ml</strong>.';
            return;
        }

        container.innerHTML = `
            <div class="row g-2 text-center">
                <div class="col-6"><div class="ml-metric-card p-2"><strong>${escapeHTML(metricas.accuracy)}</strong><br><small>Accuracy</small></div></div>
                <div class="col-6"><div class="ml-metric-card p-2"><strong>${escapeHTML(metricas.precision)}</strong><br><small>Precision</small></div></div>
                <div class="col-6"><div class="ml-metric-card p-2"><strong>${escapeHTML(metricas.recall)}</strong><br><small>Recall</small></div></div>
                <div class="col-6"><div class="ml-metric-card p-2"><strong>${escapeHTML(metricas.f1_score)}</strong><br><small>F1</small></div></div>
            </div>
            <div class="small mt-2 text-muted">Modelo: ${escapeHTML(metricas.model_name)} ${escapeHTML(metricas.model_version || '')} | Entrenado: ${escapeHTML(metricas.trained_at)}</div>
        `;
    }

    async function loadLogs() {
        try {
            const response = await api.get('/api/pacientes/logs/');
            const logs = response.data.results || response.data;
            const tbody = document.getElementById('tableLogs');
            if (!tbody) {
                return;
            }

            tbody.innerHTML = '';
            const rows = logs.map(log => `
                <tr>
                    <td>${formatDate(log.fecha_ejecucion)}</td>
                    <td>${escapeHTML(log.registros_procesados)}</td>
                    <td>${formatNumber(log.tiempo_ejecucion)}</td>
                    <td><span class="badge ${log.estado === 'Exitoso' ? 'bg-success' : 'bg-danger'}">${escapeHTML(log.estado)}</span></td>
                    <td class="logs-details">${formatLogDetails(log.detalles)}</td>
                </tr>
            `).join('');
            tbody.innerHTML = rows;
        } catch (error) {
            console.error(error);
            if (!api.isAuthError(error)) {
                showError('No fue posible cargar el histórico ETL.');
            }
        }
    }

    async function exportPatients(format) {
        try {
            const response = await api.get(`/api/analytics/export/${format}/`, { responseType: 'blob' });
            const blob = new Blob([response.data], { type: response.headers['content-type'] || 'application/octet-stream' });
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `pacientes.${format}`;
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            showError(error.response?.data?.error || 'Error al exportar datos');
        }
    }

    async function uploadCsv(event) {
        event.preventDefault();
        const form = event.target;
        const button = document.getElementById('btnUploadCsv');
        const result = document.getElementById('uploadResult');
        const data = new FormData(form);

        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Procesando...';
        result.className = 'mt-3 alert alert-info upload-result';
        result.classList.remove('d-none');
        result.textContent = 'Archivo recibido. El ETL se está ejecutando.';

        try {
            const response = await api.post('/api/pacientes/upload-csv/', data, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            result.className = 'mt-3 alert alert-success upload-result';
            result.textContent = response.data.status;
            form.reset();
            setTimeout(loadLogs, 5000);
        } catch (error) {
            result.className = 'mt-3 alert alert-danger upload-result';
            result.textContent = error.response?.data?.error || 'Error al subir archivo. Revise columnas requeridas y rangos clínicos.';
        } finally {
            button.disabled = false;
            button.innerHTML = '<i class="bi bi-upload"></i> Subir CSV/Excel y procesar ETL';
        }
    }

    async function runEtl() {
        const button = document.getElementById('btnRunEtl');
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Ejecutando...';

        try {
            await api.post('/api/pacientes/logs/run/');
            alert('Proceso ETL ejecutado. Revise el histórico de logs.');
            setTimeout(loadLogs, 5000);
        } catch (error) {
            showError(api.isAuthError(error) ? 'Sesión expirada.' : 'Error al iniciar ETL');
            if (api.isAuthError(error)) {
                redirectLogin();
            }
        } finally {
            button.disabled = false;
            button.innerHTML = '<i class="bi bi-play-fill"></i> Ejecutar ETL';
        }
    }

    async function predictRisk(event) {
        event.preventDefault();
        const formData = new FormData(event.target);
        const data = Object.fromEntries(formData.entries());
        for (const key in data) {
            data[key] = parseFloat(data[key]);
        }

        try {
            const response = await api.post('/api/ml/predict/', data);
            const resultDiv = document.getElementById('predictResult');
            const riskElement = document.getElementById('resRiesgo');
            const probabilitiesElement = document.getElementById('resProbabilidades');
            if (!resultDiv || !riskElement || !probabilitiesElement) {
                showError('No se encontró el contenedor de resultados de predicción.');
                return;
            }

            const probabilities = Object.entries(response.data.probabilidades || {})
                .map(([risk, probability]) => `${risk}: ${(probability * 100).toFixed(2)}%`)
                .join(', ');
            const explanation = (response.data.explicacion || [])
                .map(item => `${item.feature}: ${(item.importance * 100).toFixed(2)}%`)
                .join(', ');
            resultDiv.classList.remove('d-none');
            resultDiv.querySelectorAll('.prediction-explanation, .prediction-warning').forEach(element => element.remove());
            riskElement.textContent = response.data.riesgo_predicho;
            probabilitiesElement.textContent = probabilities;
            resultDiv.insertAdjacentHTML('beforeend', `<div class="prediction-explanation small mt-2"><strong>Explicación:</strong> ${escapeHTML(explanation)}</div>`);
            resultDiv.insertAdjacentHTML('beforeend', `<div class="prediction-warning small text-muted mt-1">${escapeHTML(response.data.advertencia_clinica || '')}</div>`);
        } catch (error) {
            showError(error.response?.data?.error || 'Error en predicción');
        }
    }

    function bindEvents() {
        document.querySelectorAll('[data-risk-filter]').forEach(button => {
            button.addEventListener('click', () => {
                activeRiskFilter = button.dataset.riskFilter;
                document.querySelectorAll('[data-risk-filter]').forEach(chip => chip.classList.remove('active'));
                button.classList.add('active');
                renderPacientes(pacientesRecientes);
            });
        });

        document.querySelectorAll('[data-export]').forEach(button => {
            button.addEventListener('click', () => exportPatients(button.dataset.export));
        });

        const uploadForm = document.getElementById('formUploadCsv');
        if (uploadForm) {
            uploadForm.addEventListener('submit', uploadCsv);
        }

        const runEtlButton = document.getElementById('btnRunEtl');
        if (runEtlButton) {
            runEtlButton.addEventListener('click', runEtl);
        }

        const predictForm = document.getElementById('formPredict');
        if (predictForm) {
            predictForm.addEventListener('submit', predictRisk);
        }

        const refreshLogsButton = document.getElementById('btnRefreshLogs');
        if (refreshLogsButton) {
            refreshLogsButton.addEventListener('click', loadLogs);
        }

        const patientFilter = document.getElementById('filtroPacientes');
        if (patientFilter) {
            patientFilter.addEventListener('input', () => renderPacientes(pacientesRecientes));
        }

        const clearFilterButton = document.getElementById('btnLimpiarFiltro');
        if (clearFilterButton) {
            clearFilterButton.addEventListener('click', () => {
                const filterElement = document.getElementById('filtroPacientes');
                if (filterElement) {
                    filterElement.value = '';
                }
                renderPacientes(pacientesRecientes);
            });
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        if (!api) {
            return;
        }

        api.setAuthHeader();
        bindEvents();

        if (shouldLoadAnalytics) {
            loadData();
        }

        if (isPacientes) {
            loadDashboardExtras();
        }
    });
})();
