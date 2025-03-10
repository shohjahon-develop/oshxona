from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Customer
from .serializers import CustomerSerializer

from django.contrib.auth import login
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import User

class LoginView(APIView):
    def post(self, request):
        pin_code = request.data.get("pin_code")

        if not pin_code:
            return Response({"error": "PIN kod majburiy"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pin_code=pin_code)
            login(request, user)  # Django session orqali login qilish
            return Response({
                "message": "Muvaffaqiyatli tizimga kirdingiz",
                "user": {"name": user.name, "role": user.role}
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Noto‘g‘ri PIN kod"}, status=status.HTTP_401_UNAUTHORIZED)






class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({"message": "Tizimdan chiqildi"})



class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

















































