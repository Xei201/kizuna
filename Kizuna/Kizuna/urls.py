from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

#только на период разработки
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', RedirectView.as_view(url='/general/', permanent=True)),
    path('admin/', admin.site.urls),
    path('api/v1/', include('API.urls')),
    path('general/', include('general.urls')),
    path("accounts/", include("django.contrib.auth.urls")),
]

#только на период разработки
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)