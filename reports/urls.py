from django.urls import path
from .views import OrderStatisticsView, PopularDishesView, StaffActivityView

urlpatterns = [
    path("stats/orders/", OrderStatisticsView.as_view(), name="order-stats"),
    path("stats/popular-dishes/", PopularDishesView.as_view(), name="popular-dishes"),
    path("stats/staff-activity/", StaffActivityView.as_view(), name="staff-activity"),
]
