$(document).ready(function () {
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

    $('#register-form').on('submit', function (event) {
        event.preventDefault();

        const data = {
            username: $('#username').val(),
            first_name: $('#first_name').val(),
            last_name: $('#last_name').val(),
            email: $('#email').val(),
            password1: $('#password').val(),
            password2: $('#password_check').val(),
        };

        $.ajax({
            url: 'http://127.0.0.1:8000/accounts/register/',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            headers: {
                'X-CSRFToken': csrftoken, // Додаємо CSRF-токен
            },
            success: function (response) {
                alert('Registration successful!');
                window.location.href = '/login.html'; // Редірект на сторінку логіну
            },
            error: function (xhr) {
                const errors = JSON.parse(xhr.responseText).errors || {};
                alert(`Registration failed: ${JSON.stringify(errors)}`);
            },
        });
    });
});
