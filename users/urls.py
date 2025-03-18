from django.urls import path, include
from .views import LoginView, LogoutView
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, CustomerDeliveryViewSet

router = DefaultRouter()
router.register(r'customers', CustomerViewSet)
router.register(r'customer-deliveries', CustomerDeliveryViewSet)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', include(router.urls)),
]
