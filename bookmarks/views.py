from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Bookmark, Category
from .serializers import BookmarkSerializer, CategorySerializer
from django.shortcuts import render, get_object_or_404
import logging
from rest_framework.permissions import IsAuthenticated
# from rest_framework.authentication import JWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.decorators import api_view, permission_classes, authentication_classes

logger = logging.getLogger(__name__)

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def bookmark_list(request):
    if request.method == 'GET':
        search_query = request.GET.get('searchQuery', '')
        category_id = request.GET.get('category', '')
        favorite_only = request.GET.get('favorite', '') == 'true'

        # Начальная фильтрация всех закладок
        bookmarks = Bookmark.objects.all()

        # Фильтрация по названию
        if search_query:
            bookmarks = bookmarks.filter(title__icontains=search_query)

        # Фильтрация по категории
        if category_id:
            bookmarks = bookmarks.filter(category_id=category_id)

        # Фильтрация по избранному
        if favorite_only:
            bookmarks = bookmarks.filter(favorite=True)

        serializer = BookmarkSerializer(bookmarks, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        data = request.data.copy()
        category_id = data.get("category_id", None)
        logger.info(f"Received data: {data}")
        logger.info(f"Received category_id: {category_id}")

        if category_id:
            try:
                category = Category.objects.get(id=int(category_id))
                data['category'] = category.id
                logger.info(f"Category found: {category.name}")
            except Category.DoesNotExist:
                logger.error(f"Category with ID {category_id} not found.")
                return Response({"error": "Category not found."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.error("No category provided in the request.")
            return Response({"error": "Category is required."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = BookmarkSerializer(data=data)
        if serializer.is_valid():
            bookmark = serializer.save()
            logger.info(f"Bookmark created with ID {bookmark.id}")
            return Response(BookmarkSerializer(bookmark).data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def bookmark_detail(request, pk):
    try:

        bookmark = Bookmark.objects.get(pk=pk)
    except Bookmark.DoesNotExist:

        return Response({"error": "Bookmark not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':

        serializer = BookmarkSerializer(bookmark)
        return Response(serializer.data)

    elif request.method == 'PUT':

        serializer = BookmarkSerializer(bookmark, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':

        bookmark.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def category_list(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def bookmark_detail_view(request, pk):
    bookmark = get_object_or_404(Bookmark, pk=pk)
    return render(request, 'bookmark_detail.html', {'bookmark': bookmark})
