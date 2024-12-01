from django.urls import path
from .views import register
from . import views
from rest_framework_simplejwt.views import TokenRefreshView
from .views import GetUserInfoView

urlpatterns = [
    path('login/', views.login_view, name='login'),  # Маршрут для логіну
    path('register/', register, name='register'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user-info/', GetUserInfoView.as_view(), name='user_info'),
]