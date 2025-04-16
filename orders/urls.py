# orders/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import * # Hammasini import qilish

router = DefaultRouter()
router.register(r'tables', TableViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'takeout', TakeoutViewSet)
router.register(r'delivery', DeliveryViewSet)
# Actionlar avtomatik ravishda router tomonidan qo'shiladi (masalan, /delivery/{pk}/update-status/)

urlpatterns = [
    path('', include(router.urls)),
    path('served-all/', ServedOrdersView.as_view(), name='served-all'),
    # path('my-deliveries/', MyDeliveriesView.as_view(), name='my-deliveries'), # Yetkazib beruvchi uchun yangi URL
]




# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import *
# router = DefaultRouter()
# router.register(r'tables', TableViewSet)
# router.register(r'orders', OrderViewSet)
# router.register(r'takeout', TakeoutViewSet)
# router.register(r'delivery', DeliveryViewSet)
#
#
# urlpatterns = [
#     path('', include(router.urls)),
#     path('served-all/', ServedOrdersView.as_view(), name='served-all'),
# ]
