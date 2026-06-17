document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('loginForm');
    if (form) {
        form.addEventListener('submit', handleLogin);
    }

    function handleLogin(e) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);

        fetch(form.action || '/api/auth/session-login/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
            },
        })
            .then(response => {
                if (response.ok) {
                    window.location.href = '/';
                } else {
                    console.error('Login failed');
                }
            })
            .catch(error => console.error('Error:', error));
    }
});
