from django.urls import path, re_path, include
from . import views


# API for the Bizon365 hook that activates the process of importing users to the getcourse
api_patterns = [
    path('start/', views.InitialImportAPIView.as_view(), name="transfer-bizon-gk"),
]

# Paths responsible for manually importing viewers to getcourse
hand_import_patterns = [
    path('', views.HandImportView.as_view(), name="hand-import"),
    re_path(r'^list_webinar/(?P<wq>\d+)$', views.ExportWebroomListView.as_view(), name="get-bizon-web"),
    path('list_webinar/start_import', views.HandImportViewersListView.as_view(), name="start-hand-import"),
]

# Lists of already completed imports with details and start re-import
webroom_patterns = [
    path('', views.WebroomList.as_view(), name="my-webroom"),
    re_path(r'^detail/(?P<pk>\d+)$', views.WebroomDetail.as_view(), name="detail-webroom"),
    re_path(r'^detail/(?P<pk>\d+)/reimport$', views.ImportViewersListView.as_view(), name="reimport-webroom"),
    re_path(r'^detail/(?P<pk>\d+)/upload$', views.ExportViewersCSV.as_view(), name="upload-webroom"),
]

# Here the user sets his API keys for services
setting_patterns = [
    path('', views.SettingsDelayView.as_view(), name="setting-delay"),
    path('my', views.SettingsUpdateView.as_view(), name="setting"),
    path('my/bizon', views.SettingsBizonConnectView.as_view(), name="setting-bizon"),
    path('my/bizon/session', views.WebroomSessionBizonListView.as_view(), name="list-session"),
    re_path(r'^my/bison/session/(?P<pk>\d+)', views.SessionWebroomListView.as_view(), name="session-webroom-list"),
]

# The section is responsible for corrupting users by downloading CSV
getcourse_import_patterns = [
    path('', views.CSVFileImportList.as_view(), name="my-import-getcourse"),
    path('import', views.DownloadedFileImportGetcourse.as_view(), name="import-getcourse"),
    re_path(r'^import/correct/(?P<pk>\d+)', views.ReimportFileGetcorse.as_view(), name="reimport-getcourse"),
    path('import/correct/', views.CorrectFileFieldImportGetcourse.as_view(), name="correct-field-getcourse"),
    path('import/correct/success', views.SuccessImportGetcourse.as_view(), name="success-import-getcourse"),
]

# The section converts files with tests to a convenient form
test_convert_patterns = [
    path('', views.Test_upload_data_FormView.as_view(), name="upload_test"),
]

urlpatterns = [
    path('', views.index, name="index"),
    path('api/v1/', include(api_patterns)),
    path('my_webroom/', include(webroom_patterns)),
    path('hand_import/', include(hand_import_patterns)),
    path('setting', include(setting_patterns)),
    path('import_getcourse/', include(getcourse_import_patterns)),
    path('test_convert/', include(test_convert_patterns)),
]
