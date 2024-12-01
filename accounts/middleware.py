from django.shortcuts import redirect
from django.urls import reverse

class RedirectToLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            # Шляхи, які дозволені без авторизації
            allowed_paths = [
                reverse('login'),
                reverse('register'),
                reverse('user_info'),
                '/api/token/',
                '/api/token/refresh/',
                '/api/bookmarks/',
                '/api/categories/',
                '/api/accounts/user-info/',
                '/api/accounts/',
            ]

            # Додати логіку для API-запитів
            if request.path.startswith('/api/') and not request.user.is_authenticated:
                return self.get_response(request)

            # Редірект для неавторизованих користувачів
            if hasattr(request, 'user') and not request.user.is_authenticated:
                if not any(request.path.startswith(path) for path in allowed_paths):
                    return redirect('/login.html')
        except Exception as e:
            # Логування помилок для дебагу
            print(f"Middleware error: {e}")

        return self.get_response(request)
