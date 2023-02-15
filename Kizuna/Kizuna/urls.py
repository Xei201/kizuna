from django.contrib import admin
from django.urls import path, include
#только на период разработки
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('API.urls')),
]

#только на период разработки
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)