from django.urls import path
from . import views

urlpatterns = [
    path('bookmarks/', views.bookmark_list, name='bookmark_list_api'),  # API для списка закладок
    path('bookmarks/<int:pk>/', views.bookmark_detail, name='bookmark_detail_api'),  # API для одной закладки
    path('categories/', views.category_list, name='category_list_api'),  # API для списка категорий
    path('view/<int:pk>/', views.bookmark_detail_view, name='bookmark_detail_view'),  # Новый маршрут для просмотра
]
