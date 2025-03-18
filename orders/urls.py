from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
router = DefaultRouter()
router.register(r'tables', TableViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'takeout', TakeoutViewSet)
router.register(r'delivery', DeliveryViewSet)
router.register(r'order-items', OrderItemViewSet)
router.register(r'takeout-items', TakeoutItemViewSet)
router.register(r'delivery-items', DeliveryItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
