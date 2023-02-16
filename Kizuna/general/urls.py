from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('my_webroom/', views.WebroomList.as_view(), name="my-webroom"),
    path('hand_import/', views.hand_import, name="hand-import"),
    re_path(r'^hand_import/list_webinar/(?P<wq>\d+)$', views.get_bizon_web, name="get-bizon-web"),
    path('hand_import/list_webinar/start_import', views.hand_import_start, name="start-hand-import"),
]