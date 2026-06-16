(function () {
    const api = window.HealthAnalyticsAPI;

    function escapeHTML(value) {
        if (value === null || value === undefined) return '';
        return String(value)
            .replaceAll('&', '&amp;')
            .replaceAll('<', '<')
            .replaceAll('>', '>')
            .replaceAll('"', '"')
            .replaceAll("'", '&#039;');
    }

    function showError(msg) {
        alert(msg);
    }

    function getSelectedRadioValue(name) {
        const checked = document.querySelector(`input[name="${name}"]:checked`);
        return checked ? checked.value : null;
    }

    async function downloadReport({ export_type, format }) {
        // export_type se mantiene por compatibilidad con la UI,
        // pero por ahora la exportación disponible es de pacientes.
        // Se centraliza en reports y se puede ampliar luego.
        const url = `/api/reportes/export/${encodeURIComponent(format)}/`;

        const response = await api.get(url, { responseType: 'blob' });
        const blob = new Blob([response.data], {
            type: response.headers['content-type'] || 'application/octet-stream',
        });

        const cd = response.headers['content-disposition'] || '';
        let filename = `reporte.${format}`;
        const match = cd.match(/filename=\"?([^\"]+)\"?/i);
        if (match && match[1]) filename = match[1];

        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(link.href);
    }

    async function downloadBlob({ url, params, filename, mimeType }) {
        const response = await api.get(url, { responseType: 'blob', params });
        const blob = new Blob([response.data], {
            type: mimeType || response.headers['content-type'] || 'application/octet-stream',
        });

        const cd = response.headers['content-disposition'] || '';
        let finalName = filename;
        const match = cd.match(/filename=\"?([^\"]+)\"?/i);
        if (match && match[1]) finalName = match[1];

        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = finalName;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(link.href);
    }

    function bindPdfForm() {
        const form = document.getElementById('formPdf');
        if (!form) return;

        form.addEventListener('submit', async (event) => {
            event.preventDefault();

            const periodo = form.querySelector('[name="periodo"]')?.value || 'mes';
            const include_kpis = form.querySelector('[name="include_kpis"]')?.checked;
            const include_charts = form.querySelector('[name="include_charts"]')?.checked;
            const include_table = form.querySelector('[name="include_table"]')?.checked;

            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                const old = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Generando...';

                try {
                    const url = '/api/reportes/export/pdf/';
                    await downloadBlob({
                        url,
                        params: {
                            periodo,
                            include_kpis,
                            include_charts,
                            include_table,
                        },
                        filename: `reporte_${periodo}.pdf`,
                        mimeType: 'application/pdf',
                    });
                } catch (e) {
                    showError(e.response?.data?.error || 'Error al generar el PDF');
                } finally {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = old;
                }
            }
        });
    }

    function bindExportForm() {
        const form = document.getElementById('formExport');
        if (!form) return;

        form.addEventListener('submit', async (event) => {
            event.preventDefault();

            const export_type = form.querySelector('[name="export_type"]')?.value || 'patients';
            const format = getSelectedRadioValue('format');

            if (!format) {
                showError('Seleccione un formato de exportación.');
                return;
            }

            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                const old = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Descargando...';

                try {
                    const url = `/api/reportes/export/${encodeURIComponent(format)}/`;
                    await downloadBlob({
                        url,
                        params: {
                            export_type,
                        },
                        filename: `reporte_${export_type}.${format}`,
                        mimeType: format === 'xlsx' ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' : 'text/csv',
                    });
                } catch (e) {
                    showError(e.response?.data?.error || 'Error al descargar el reporte');
                } finally {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = old;
                }
            }
        });
    }

    document.addEventListener('DOMContentLoaded', () => {
        if (!api) return;
        api.setAuthHeader();
        bindPdfForm();
        bindExportForm();
    });
})();


