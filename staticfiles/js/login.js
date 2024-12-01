$(document).ready(function () {
    $('#login-form').on('submit', function (event) {
        event.preventDefault();
    
        const data = {
            username: $('#username').val(),
            password: $('#password').val(),
        };
    
        $.ajax({
            url: 'http://127.0.0.1:8000/api/token/',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function (response) {
                // Збереження токенів у localStorage
                localStorage.setItem('access_token', response.access);
                localStorage.setItem('refresh_token', response.refresh);
    
                // Редірект на головну сторінку
                window.location.href = '/index.html';
            },
            error: function (xhr) {
                alert('Login failed: ' + xhr.responseText);
            },
        });
    });    

    // Перевіряємо, чи користувач залогінений
    const token = localStorage.getItem('access_token');
    if (token) {
        window.location.href = '/index.html';
    }
});