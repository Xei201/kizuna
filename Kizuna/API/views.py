import csv
import logging
import datetime
import uuid
from os import path

from django.db import transaction
from django.http import HttpResponse
from django.views.generic import TemplateView
from rest_framework import generics, status
from urllib.parse import urlencode
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.encoding import force_str
from django.views import generic, View
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response

from Kizuna import settings
from .core.exceptions import NoModelFoundException, NoCorrectPermission
from .core.export_csv import ExportCSV
from .core.import_logic import ImportGetcorseValidation, ImportGetcourseValidationPK, ConvertedTestCSV
from .core.request_service import RequestBizon, RequestGetcorse
from .core.serializers import WebroomSerializer
from .core.permissions import SuccessToken
from .forms import QuantityWebroom, SettingForm, DownLoadedFileForm, CorrectFieldsForm, DownLoadedTestFileForm, \
    CreateTrackedSessionForm
from .models import WebroomTransaction, ViewersImport, TokenImport, FileImportGetcourse, TrackedSessinBizon


logger = logging.getLogger(__name__)


# API for the Bizon365 hook that activates the process of importing users to the getcourse
class InitialImportAPIView(generics.CreateAPIView):
    """API responsible for importing people from Bizon to Getcourse"""

    model = WebroomTransaction
    serializer_class = WebroomSerializer
    permission_classes = (SuccessToken, )

    def create(self, *args, **kwargs):
        """Running the export and export people class"""

        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        webroom = serializer.data["webinarId"]
        # Next, the export of people from the Bizon365 platform starts from the beginning
        # and then their import to the Getcourse platform
        export = RequestBizon(self.request)
        if export.export_viwers(webroom):
            imp = ImportGetcorseValidation(self.request)
            imp.start_import_to_getcourse_api(webroom)
        else:
            logger.warning(f"Fallen API import to Getcourse viewers from API to Bizon "
                        f"request {self.request}")
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        """Matching the token with the user"""

        user_id = TokenImport.objects.get(token=self.request.GET.get('token')).user
        logger.info(f"Initiation API import to Getcourse viewers from API to Bizon "
                    f"request {self.request}")
        serializer.save(user_id=user_id)


@login_required
@permission_required("API.can_request", raise_exception=True)
def index(request):
    """View displaying general statistics data"""

    webroom_all = WebroomTransaction.objects.all().count()
    webroom_quantity = WebroomTransaction.objects.filter(user_id=request.user).count()
    return render(request, "index.html", context={
        "webroom_all": webroom_all,
        "webroom_quantity": webroom_quantity,
    })


class WebroomList(PermissionRequiredMixin, generic.ListView):
    """List of webinars imported by the user"""

    model = WebroomTransaction
    context_object_name = "webrooms"
    template_name = 'webroom/list_webroom.html'
    paginate_by = 10
    permission_required = ("API.can_request",)

    def get_queryset(self):
        user_id = self.request.user
        return WebroomTransaction.objects.filter(user_id=user_id).order_by('create')


class WebroomDetail(PermissionRequiredMixin, generic.DetailView):
    """Data for a specific user import"""

    template_name = "webroom/detail_webroom.html"
    context_object_name = "webroom"
    permission_required = ("API.can_request",)

    def get_object(self):
        return get_object_or_404(WebroomTransaction, pk=self.kwargs.get('pk'))


class ImportViewersListView(PermissionRequiredMixin, generic.ListView):
    """Re-importing to the getcourse is being carried out,
    after which a list of users is displayed """

    model = ViewersImport
    template_name = 'webroom/list_viewers.html'
    context_object_name = "list_viewers"
    permission_required = ("API.can_request",)
    paginate_by = 20

    def get_queryset(self):
        webinarId = self._get_webinar_id()
        if self._import_gk(webinarId):
            pk = WebroomTransaction.objects.get(webinarId=webinarId).id
            return ViewersImport.objects.filter(webroom=pk)
        else:
            dict_error = ["Error", "Connection Error, try later"]
            return dict_error

    def _get_webinar_id(self):
        return get_object_or_404(WebroomTransaction, pk=self.kwargs.get('pk')).webinarId

    def _import_gk(self, webinarId: str) -> bool:
        """Transfer to a separate method is made for the convenience
        of adjusting the VIEW operation during inheritance"""

        imp = RequestGetcorse(self.request)
        return imp.import_viewers(webinarId)


class ExportViewersCSV(PermissionRequiredMixin, ExportCSV):
    """Generates a CSV file with a list of imported people"""

    model = ViewersImport
    field_names = ["name", "email", "phone", "view", "buttons", "banners", "create"]
    add_col_names = True
    col_names = ["Имя", "Почта", "Телефон", "Время", "Кнопки", "Баннеры", "Создан"]
    permission_required = ("API.can_request",)

    def get_queryset(self):
        user = self.request.user
        webroom = get_object_or_404(WebroomTransaction, pk=self.kwargs.get('pk'))
        if webroom.user_id != user:
            exception_msg = "No permission"
            logger.warning(f"{user} The user tried to download the "
                           f"CSV file of someone else's webinar {self.kwargs.get('pk')}")
            raise NoCorrectPermission(_(exception_msg))
        queryset = webroom.viewersimport_set.all()
        if queryset.exists():
            return webroom.viewersimport_set.iterator()
        else:
            logger.warning(f"{user} no find model to get queryset from CSV")
            exception_msg = "No model to get queryset from. Either provide " \
                            "a model or override get_queryset method."
            raise NoModelFoundException(_(exception_msg))
        logger.info(f"{user} create CSV file {self.filename}")

    def get_filename(self):
        """The filename can be set by default or generated in this method"""

        if self.filename is not None:
            return self.filename
        if self.model is not None:
            pk = self.kwargs.get('pk')
            model_name = get_object_or_404(WebroomTransaction, pk=pk).__str__().lower()
            self.filename = force_str(model_name + '_list.csv')
        else:
            logger.warning(f"No find model to generate filename from CSV")
            exception_msg = "No model to generate filename. Either provide " \
                            "model or filename or override get_filename " \
                            "method."
            raise NoModelFoundException(_(exception_msg))
        return self.filename

    def get(self, request, pk):
        return self._create_csv()


# Paths responsible for manually importing viewers to getcourse
class HandImportView(PermissionRequiredMixin, generic.edit.FormView):
    """Form for receiving webinar list request parameters"""

    template_name = 'webroom/get_webroom.html'
    form_class = QuantityWebroom
    permission_required = ("API.can_request",)

    def form_valid(self, form):
        self.form = form
        return super().form_valid(form)

    def get_success_url(self):
        wq = self.form.cleaned_data['quantity_webroom']
        params = {"date_min": self.form.cleaned_data["date_min"],
                  "date_max": self.form.cleaned_data["date_max"]}
        return reverse("get-bizon-web", args=[str(wq)]) + '?' + urlencode(params)

    def get_initial(self):
        initial = super().get_initial()
        initial["quantity_webroom"] = 1
        initial["date_min"] = datetime.date.today() - datetime.timedelta(weeks=4)
        initial["date_max"] = datetime.date.today()
        return initial


# Lists of already completed imports with details and start re-import
class ExportWebroomListView(PermissionRequiredMixin, generic.ListView):
    """List of webnars as part of manual import"""

    model = None
    template_name = 'webroom/response_webroom.html'
    context_object_name = "list_webinar"
    permission_required = ("API.can_request",)
    paginate_by = 10

    def get_queryset(self):
        webroom_quantity = int(self.kwargs.get("wq"))
        # Start uploading data from bison365
        export = RequestBizon(self.request)
        list_webinar = export.get_web_list(webroom_quantity)
        return list_webinar


class HandImportViewersListView(ImportViewersListView):
    """List of users imported manually"""

    @transaction.atomic
    def _get_webinar_id(self):
        webinarId = self.request.GET.get('webinarId')
        # Check to avoid collisions in case of import of the same object
        if not WebroomTransaction.objects.filter(webinarId=webinarId).exists():
            webroom = WebroomTransaction()
            webroom.event = self.request.GET.get('event')
            webroom.roomid = self.request.GET.get('roomid')
            webroom.webinarId = webinarId
            webroom.user_id = self.request.user
            webroom.save()
        return webinarId

    def _import_gk(self, webinarId: str) -> bool:
        export = RequestBizon(self.request)
        if not export.export_viwers(webinarId):
            return False
        return super()._import_gk(webinarId)


# Here the user sets his API keys for services
class SettingsUpdateView(PermissionRequiredMixin, generic.edit.UpdateView):
    """External services token setup page"""

    model = TokenImport
    form_class = SettingForm
    permission_required = ("API.can_request",)
    template_name = "setting/setting_form.html"
    success_url = reverse_lazy("setting")

    # Получение объекта через авторизованого юзера
    def get_object(self, queryset=None):
        return TokenImport.objects.get(user=self.request.user)


class SettingsDelayView(PermissionRequiredMixin, generic.DetailView):
    """View of user tokens"""

    model = TokenImport
    fields = ["token_gk", "name_gk", "token_bizon"]
    permission_required = ("API.can_request",)
    template_name = "setting/setting_delay.html"
    context_object_name = "user_token"

    # Получение объекта через авторизованого юзера
    def get_object(self, queryset=None):
        return TokenImport.objects.get(user=self.request.user)


class SettingsBizonConnectView(PermissionRequiredMixin, TemplateView):
    """Generates a webhook after the end of the webinar on bison"""

    permission_required = ("API.can_request",)
    template_name = "setting/setting_bizon_webhook.html"

    def get_context_data(self, **kwargs):
        context = {}
        token = TokenImport.objects.get(user=self.request.user).token
        url = path.join(settings.URL_SERVER, settings.URL_API_INTEGRATION, ("?token=" + str(token)))
        context["url_api"] = url
        return context


# The section is responsible for corrupting users by downloading CSV
class DownloadedFileImportGetcourse(PermissionRequiredMixin, generic.CreateView):
    """CSV upload form to import users on Getcourse"""

    permission_required = ("API.can_request",)
    template_name = 'import_gk/downloaded_file.html'
    form_class = DownLoadedFileForm
    success_url = reverse_lazy('correct-field-getcourse')

    def form_valid(self, form):
        """Add user params"""

        form.instance.user = self.request.user
        return super().form_valid(form)


class CorrectFileFieldImportGetcourse(PermissionRequiredMixin, generic.edit.FormVie):
    """The user selects the ratio of the fields in the last uploaded CSV file
    and the fields of the import model"""

    permission_required = ("API.can_request",)
    template_name = 'import_gk/correct_field_params.html'
    form_class = CorrectFieldsForm
    success_url = reverse_lazy('success-import-getcourse')
    import_validation_class = ImportGetcorseValidation

    def get(self, request, *args, **kwargs):
        """Add choices from a CSV file to a form"""

        context_data = self.get_context_data()
        self.get_coices_for_form(request, context_data["form"], **kwargs)
        return self.render_to_response(context_data)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        # Loading choices form fields
        self.get_coices_for_form(request, form, **kwargs)
        if form.is_valid():
            field_position_dict = form.cleaned_data
            user = request.user
            file_data = FileImportGetcourse.objects.filter(user=user).last()
            # The name of the import is combined from the group for the export and the date the file was loaded,
            # it is necessary to avoid collisions when loading imports with the same data
            webroom = file_data.group_user + str(file_data.date_load)
            group = file_data.group_user
            imp = self.get_import_validation_class(request=request, **kwargs)
            # Checking the correctness of data from CSV import into the database
            if imp.start_upload_viewers_csv_to_bd(field_position_dict):
                # Start import to Getcourse
                imp.start_import_to_getcorse_csv(webroom, group=group)
                return self.form_valid(form)

        return self.form_invalid(form)

    def get_coices_for_form(self, request, form, **kwargs):
        """Loading file fields for a select form linking an import field to a form field """
        imp = self.get_import_validation_class(request, **kwargs)
        list_choices_tuple = imp.get_choices_field()
        form.fields['email'].choices = list_choices_tuple
        form.fields['name'].choices = list_choices_tuple
        form.fields['phone'].choices = list_choices_tuple

    def get_import_validation_class(self, request, **kwargs):
        """Return the import validation class to use"""

        return self.import_validation_class(request, **kwargs)


class SuccessImportGetcourse(PermissionRequiredMixin, TemplateView):
    """Page after import completed on Getcourse"""

    permission_required = ("API.can_request",)
    template_name = 'import_gk/success_import.html'


class CSVFileImportList(PermissionRequiredMixin, generic.ListView):
    """List of CSV files imported by the user"""

    model = WebroomTransaction
    context_object_name = "files"
    template_name = 'import_gk/list_csv_file.html'
    paginate_by = 10
    permission_required = ("API.can_request",)

    def get_queryset(self):
        user_id = self.request.user
        return FileImportGetcourse.objects.filter(user_id=user_id)


class ReimportFileGetcorse(CorrectFileFieldImportGetcourse):
    """The user selects the ratio of the fields in the selected CSV file
    and the fields of the import model"""

    # The file is loaded not from the user,
    # but from the database through changes in the file validation class
    import_validation_class = ImportGetcourseValidationPK


# The section converts files with tests to a convenient form
class TestUploadTestFormView(PermissionRequiredMixin, generic.edit.FormVie):
    """Loading a user test file to process it and bring it to a valid form"""

    form_class = DownLoadedTestFileForm
    template_name = 'test_convert/downloaded_test_file.html'
    permission_required = ("API.can_request",)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            file = form.cleaned_data['file']

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(
                force_str(str(uuid.uuid4()) + '_list.csv'))

            try:
                wr = csv.writer(
                    response,
                    dialect='excel'
                )
            except TypeError:
                raise TypeError()

            # Runs a class for converting data into the correct form
            converted_data = ConvertedTestCSV.convert_data(file)
            wr.writerows(converted_data)
            logger.info(response)
            return response


class WebroomSessionBizonListView(PermissionRequiredMixin, generic.ListView):
    """List of tracked webinar sessions"""

    model = TrackedSessinBizon
    permission_required = ("API.can_request",)
    context_object_name = "sessions"
    template_name = "session/bizon_vebroom_list_tracked.html"
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        return TrackedSessinBizon.objects.filter(user=user)


class SessionWebroomListView(PermissionRequiredMixin, generic.DetailView):
    """List webroom in session"""

    model = TrackedSessinBizon
    permission_required = ("API.can_request",)
    context_object_name = "session"
    template_name = "session/session_bizon.html"

    # Add chek user permission
    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        return TrackedSessinBizon.objects.prefetch_related("webroomtransaction_set").get(pk=pk)


class WebroomSessionCreateView(PermissionRequiredMixin, generic.CreateView):
    """Create tracked session of webinar"""

    model = TrackedSessinBizon
    permission_required = ("API.can_request",)
    form_class = CreateTrackedSessionForm
    success_url = reverse_lazy('list-session')
    template_name = "session/session_webinar_create.html"

    def form_valid(self, form):
        """Add user params"""

        form.instance.user = self.request.user
        logger.info(f"{self.request.user} create new session {form.clean_session()}")

        return super().form_valid(form)


class JoinTrackedSessionWithWebroom(PermissionRequiredMixin, View):
    """Searches for webroom import matching session criteria"""

    permission_required = ("API.can_request",)

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        user = request.user
        session = TrackedSessinBizon.objects.get(pk=pk)
        WebroomTransaction.objects.filter(
            user_id=user,
            session=None,
            roomid=session.session).update(session=session.id)
        logger.info(f"{request.user} start search webroom for session {session.session}")

        url = reverse("session-bizon", args=pk)
        return redirect(url)

