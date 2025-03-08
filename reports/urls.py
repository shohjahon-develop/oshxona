from django.urls import path
from .views import *

urlpatterns = [
    path("stats/orders/", OrderStatisticsView.as_view(), name="order-stats"),
    path("stats/popular-dishes/", PopularDishesView.as_view(), name="popular-dishes"),
    path("stats/staff-activity/", EmployeeActivityReport.as_view(), name="staff-activity"),
]
