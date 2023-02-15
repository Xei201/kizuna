from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'start/$', views.InitialImportAPIView.as_view(), name="transfer-bizon-gk"),
]