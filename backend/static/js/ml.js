(function () {
    const api = window.HealthAnalyticsAPI;

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

    function setText(id, value, fallback = '-') {
        const el = document.getElementById(id);
        if (!el) return;
        el.textContent = value === null || value === undefined || value === '' ? fallback : value;
    }

    function renderConfusionMatrix(confusionMatrix, labels) {
        const canvas = document.getElementById('chartConfusionMatrix');
        if (!canvas) return;

        const parent = canvas.parentElement;
        if (!parent) return;

        // Remove previous table
        const existing = parent.querySelector('#confusionMatrixTable');
        if (existing) existing.remove();

        if (!confusionMatrix || !Array.isArray(confusionMatrix) || confusionMatrix.length === 0) {
            const div = document.createElement('div');
            div.id = 'confusionMatrixTable';
            div.className = 'small text-muted mt-2';
            div.textContent = 'Sin matriz de confusión disponible.';
            parent.appendChild(div);
            return;
        }

        const size = confusionMatrix.length;
        const classLabels = labels && Array.isArray(labels) ? labels.slice(0, size) : null;
        
        let rowLabels;
        if (classLabels) {
            rowLabels = classLabels;
        } else {
            rowLabels = ['Bajo', 'Medio', 'Alto', 'Crítico'].slice(0, size);
        }
        const colLabels = rowLabels;

        let html = '<table class="table table-sm mb-0">';
        html += '<thead><tr><th></th>' + colLabels.map(l => `<th class="text-center">${escapeHTML(l)}</th>`).join('') + '</tr></thead>';
        html += '<tbody>';

        for (let i = 0; i < size; i++) {
            html += '<tr>';
            html += `<th class="text-center">${escapeHTML(rowLabels[i])}</th>`;
            for (let j = 0; j < (confusionMatrix[i] ? confusionMatrix[i].length : 0); j++) {
                html += `<td class="text-center">${escapeHTML(confusionMatrix[i][j])}</td>`;
            }
            html += '</tr>';
        }

        html += '</tbody></table>';

        const table = document.createElement('div');
        table.id = 'confusionMatrixTable';
        table.className = 'table-responsive mt-2';
        table.innerHTML = html;
        parent.appendChild(table);
    }

    async function loadMLSection() {
        if (!api) return;

        // Asegura que el header Authorization esté presente antes de leer.
        if (typeof api.setAuthHeader === 'function') {
            api.setAuthHeader();
        }

        try {
            const response = await api.get('/api/analytics/dashboard-extras/');
            const data = response.data || {};
            const metricas = data.ml_metricas;

            // Cards de precisión/recall/f1
            setText('mlAccuracy', metricas ? metricas.accuracy : '-', '-');
            setText('mlRecall', metricas ? metricas.recall : '-', '-');
            setText('mlF1', metricas ? metricas.f1_score : '-', '-');

            // Entrenamiento
            setText('mlAlgorithm', metricas ? metricas.model_name : '-', '-');
            setText('mlDataset', metricas ? metricas.dataset : '-', '-');
            setText('mlLastUpdate', metricas ? metricas.trained_at : '-', '-');
            setText('mlVersion', metricas ? metricas.model_version : '1.0', '1.0');

            // Matriz de confusión
            renderConfusionMatrix(metricas ? metricas.confusion_matrix : null, metricas ? metricas.classes : null);
        } catch (error) {
            // No rompa la UI si falla, pero hazlo visible en la matriz
            // en lugar de dejar el panel silenciosamente vacío.
            console.error(error);
            const canvas = document.getElementById('chartConfusionMatrix');
            const parent = canvas ? canvas.parentElement : null;
            if (parent && !parent.querySelector('#confusionMatrixTable')) {
                const div = document.createElement('div');
                div.id = 'confusionMatrixTable';
                div.className = 'small text-danger mt-2';
                const code = error && error.response ? ` (HTTP ${error.response.status})` : '';
                div.textContent = `No se pudieron cargar las métricas del modelo${code}.`;
                parent.appendChild(div);
            }
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        // Solo cargar si realmente estamos en ml.html
        if (document.getElementById('mlAccuracy') || document.getElementById('chartConfusionMatrix')) {
            loadMLSection();
        }
    });
})();