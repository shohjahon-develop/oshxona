from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
router = DefaultRouter()
router.register(r'tables', TableViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'takeout', TakeoutViewSet)
router.register(r'delivery', DeliveryViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
