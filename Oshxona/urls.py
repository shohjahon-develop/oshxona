from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('users.urls')),
    path('api/v2/', include('menu.urls')),
    path('api/v3/', include('orders.urls')),
    path('api/v4/', include('payments.urls')),
    path("api/reports/", include("reports.urls")),
    path("api/roles/", include("roles.urls")),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
