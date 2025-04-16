# reports/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    # Dashboard URLs
    path("dashboard/summary/", DashboardSummaryView.as_view(), name="dashboard-summary"),
    path("dashboard/weekly-sales/", WeeklySalesView.as_view(), name="dashboard-weekly-sales"),
    path("dashboard/top-products/", TopProductsView.as_view(), name="dashboard-top-products"), # period=daily/weekly/monthly
    path("dashboard/recent-orders/", RecentOrdersView.as_view(), name="dashboard-recent-orders"), # limit=N

    # Hisobotlar Sahifasi URLs
    path("general/", GeneralReportView.as_view(), name="report-general"), # period=daily/weekly/monthly/yearly
    path("products/", ProductReportView.as_view(), name="report-products"), # period=daily/weekly/monthly/yearly
    path("staff/", StaffReportView.as_view(), name="report-staff"),       # period=daily/weekly/monthly/yearly
    path("customers/", CustomerReportView.as_view(), name="report-customers"), # period=daily/weekly/monthly/yearly

    # Eski URLlar (agar hali ham kerak bo'lsa)
    path("stats/orders/", OrderStatisticsView.as_view(), name="order-stats"),
    # path("stats/popular-dishes/", PopularDishesView.as_view(), name="popular-dishes"), # TopProductsView bilan deyarli bir xil
    # path("stats/staff-activity/", EmployeeActivityReport.as_view(), name="staff-activity"), # StaffReportView ga almashtirildi
]


# from django.urls import path
# from .views import *
#
# urlpatterns = [
#     path("stats/orders/", OrderStatisticsView.as_view(), name="order-stats"),
#     path("stats/popular-dishes/", PopularDishesView.as_view(), name="popular-dishes"),
#     path("stats/staff-activity/", EmployeeActivityReport.as_view(), name="staff-activity"),
# ]
