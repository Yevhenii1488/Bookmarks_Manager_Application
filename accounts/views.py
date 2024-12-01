from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .forms import RegistrationForm
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

@csrf_exempt  # Вимикає CSRF-захист для тестування, увімкніть його в продакшені
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)  # Отримуємо JSON-дані
        form = RegistrationForm(data)
        if form.is_valid():
            form.save()
            return JsonResponse({"message": "User registered successfully"}, status=201)
        else:
            return JsonResponse({"errors": form.errors}, status=400)
    return JsonResponse({"error": "GET method not allowed"}, status=405)


def login_view(request):
    return render(request, 'login.html')


class GetUserInfoView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        })
