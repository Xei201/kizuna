from django.contrib import admin
from django.urls import path, include
#только на период разработки
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('API.urls')),
    path('general/', include('general.urls')),
    path("accounts/", include("django.contrib.auth.urls")),
]

#только на период разработки
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)