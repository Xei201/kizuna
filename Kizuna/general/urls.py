from django.urls import path, re_path, include
from . import views

hand_import_patterns = [
    path('', views.hand_import, name="hand-import"),
    re_path(r'^list_webinar/(?P<wq>\d+)$', views.ExportWebroomListView.as_view(), name="get-bizon-web"),
    path('list_webinar/start_import', views.HandImportViewersListView.as_view(), name="start-hand-import"),
]

webroom_patterns = [
    path('', views.WebroomList.as_view(), name="my-webroom"),
    re_path('^detail/(?P<pk>\d+)$', views.WebroomDetail.as_view(), name="detail-webroom"),
    re_path('^detail/(?P<pk>\d+)/reimpotr$', views.ImportViewersListView.as_view(), name="reimport-webroom"),
    re_path('^detail/(?P<pk>\d+)/upload$', views.ExportViewersCSV.as_view(), name="upload-webroom"),
]

urlpatterns = [
    path('', views.index, name="index"),
    path('my_webroom/', include(webroom_patterns)),
    path('hand_import/', include(hand_import_patterns)),
]
