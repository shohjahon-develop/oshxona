from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken

from .models import *
from .serializers import CustomerSerializer, CustomerDeliverySerializer, LoginSerializer, UserSerializer, \
    EmployeeSerializer, SettingSerializer

from django.contrib.auth import login
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import User

class LoginView(APIView):
    @swagger_auto_schema(request_body=LoginSerializer,
                         responses={200: UserSerializer,
                                    400: 'Noto‘g‘ri ma’lumotlar'})
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            pin_code = serializer.validated_data['pin_code']

            try:
                user = User.objects.get(pin_code=pin_code)

                # JWT token yaratish
                refresh = RefreshToken.for_user(user)
                user_serializer = UserSerializer(user)
                return Response({
                    "message": "Muvaffaqiyatli tizimga kirdingiz",
                    "user": user_serializer.data,  # To'liq user ma'lumotlari
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                }, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "Noto‘g‘ri PIN kod"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()  # Tokenni bekor qilish (agar blacklist ishlatilsa)
            return Response({"message": "Tizimdan chiqildi"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Xatolik yuz berdi"}, status=status.HTTP_400_BAD_REQUEST)



class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]



class CustomerDeliveryViewSet(viewsets.ModelViewSet): # ReadOnlyModelViewSet o'rniga ModelViewSet
    queryset = CustomerDelivery.objects.all()
    serializer_class = CustomerDeliverySerializer
    # Permissionni o'zgartiramiz: Autentifikatsiyadan o'tganlar ko'rishi, adminlar o'zgartirishi mumkin
    # Yoki IsAuthenticatedOrReadOnly - hamma ko'rishi, faqat ro'yxatdan o'tganlar o'zgartirishi
    permission_classes = [IsAuthenticatedOrReadOnly] # Yoki [IsAuthenticated, IsAdminOrReadOnly] yoki [IsAuthenticated]



class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(role__in=["waiter", "chef", "cashier", "cleaner"])  # Faqat xodimlarni olish
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]  # Faqat adminlar ko'rishi va o'zgartirishi mumkin


class SettingAPIView(generics.RetrieveUpdateAPIView):
    queryset = Setting.objects.all()
    serializer_class = SettingSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_object(self):
        return self.queryset.first()  # Faqat bitta sozlama obyekti bo'lishi kerak







































