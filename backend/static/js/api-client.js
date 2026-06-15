(function () {
    if (typeof axios === 'undefined') {
        return;
    }

    const TOKEN_KEY = 'access_token';
    const REFRESH_KEY = 'refresh_token';

    axios.defaults.xsrfCookieName = 'csrftoken';
    axios.defaults.xsrfHeaderName = 'X-CSRFToken';

    function getAccessToken() {
        return localStorage.getItem(TOKEN_KEY);
    }

    function getRefreshToken() {
        return localStorage.getItem(REFRESH_KEY);
    }

    function setAuthHeader() {
        const token = getAccessToken();
        if (token) {
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        } else {
            delete axios.defaults.headers.common['Authorization'];
        }
    }

    function clearAuth() {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(REFRESH_KEY);
        delete axios.defaults.headers.common['Authorization'];
    }

    function isAuthError(error) {
        return error && error.response && [401, 403].includes(error.response.status);
    }

    function get(url, config) {
        return axios.get(url, config);
    }

    function post(url, data, config) {
        return axios.post(url, data, config);
    }

    window.HealthAnalyticsAPI = {
        TOKEN_KEY,
        REFRESH_KEY,
        getAccessToken,
        getRefreshToken,
        setAuthHeader,
        clearAuth,
        isAuthError,
        get,
        post
    };

    document.addEventListener('DOMContentLoaded', setAuthHeader);
})();
