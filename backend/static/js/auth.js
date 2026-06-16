(function () {
    const api = window.HealthAnalyticsAPI;

    function showLoginError(message) {
        const existing = document.getElementById('loginError');
        if (existing) {
            existing.remove();
        }

        const alert = document.createElement('div');
        alert.id = 'loginError';
        alert.className = 'alert alert-danger mt-3 mb-0';
        alert.textContent = message;
        document.querySelector('.login-card').appendChild(alert);
    }

    function getErrorMessage(error) {
        if (error?.response?.data?.detail) {
            return error.response.data.detail;
        }

        if (error?.response?.data?.non_field_errors) {
            return error.response.data.non_field_errors.join(' ');
        }

        if (error?.response?.data?.message) {
            return error.response.data.message;
        }

        return 'Credenciales inválidas';
    }

    document.addEventListener('DOMContentLoaded', () => {
        const form = document.getElementById('loginForm');
        if (!form) {
            return;
        }

        form.addEventListener('submit', async (event) => {
            event.preventDefault();

            if (!api) {
                showLoginError('No se pudo inicializar el cliente de autenticación.');
                return;
            }

            const submitButton = form.querySelector('button[type="submit"]');
            const originalText = submitButton?.innerHTML;
            if (submitButton) {
                submitButton.disabled = true;
            }
            showLoginError('Iniciando sesión...');

            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            try {
                const response = await api.post('/api/auth/login/', data);
                localStorage.setItem(api.TOKEN_KEY, response.data.access);
                localStorage.setItem(api.REFRESH_KEY, response.data.refresh);
                api.setAuthHeader();

                await api.post('/api/auth/session-login/', formData);
                window.location.href = '/';
            } catch (error) {
                showLoginError(getErrorMessage(error));
            } finally {
                if (submitButton) {
                    submitButton.disabled = false;
                }
                if (originalText) {
                    submitButton.innerHTML = originalText;
                }
            }
        });
    });
})();
