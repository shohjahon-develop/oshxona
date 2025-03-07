from django.urls import path
from .views import RevenueStatsView, ProductStatsView

urlpatterns = [
    path("revenue-stats/", RevenueStatsView.as_view(), name="revenue-stats"),
    path("product-stats/", ProductStatsView.as_view(), name="product-stats"),
]
