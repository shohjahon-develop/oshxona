# reports/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    # Dashboard URLs
    path("dashboard/summary/", DashboardSummaryView.as_view(), name="dashboard-summary"),
    path("dashboard/weekly-sales/", WeeklySalesView.as_view(), name="dashboard-weekly-sales"),
    path("dashboard/top-products/", TopProductsView.as_view(), name="dashboard-top-products"),
    path("dashboard/recent-orders/", RecentOrdersView.as_view(), name="dashboard-recent-orders"),

    # Hisobotlar Sahifasi URLs
    path("general/", GeneralReportView.as_view(), name="report-general"),
    path("products/", ProductReportView.as_view(), name="report-products"),
    path("staff/", StaffReportView.as_view(), name="report-staff"),
    path("customers/", CustomerReportView.as_view(), name="report-customers"),

    # Eski URLlar (keraklilari qoladi)
    path("stats/orders/", OrderStatisticsView.as_view(), name="order-stats"),
    path("stats/popular-dishes/", PopularDishesView.as_view(), name="popular-dishes"), # TopProductsView ga o'xshash bo'lsa ham qoldiramiz
    # StaffActivityReport URL olib tashlandi
    # path("stats/staff-activity/", EmployeeActivityReport.as_view(), name="staff-activity"),
]


# from django.urls import path
# from .views import *
#
# urlpatterns = [
#     path("stats/orders/", OrderStatisticsView.as_view(), name="order-stats"),
#     path("stats/popular-dishes/", PopularDishesView.as_view(), name="popular-dishes"),
#     path("stats/staff-activity/", EmployeeActivityReport.as_view(), name="staff-activity"),
# ]
