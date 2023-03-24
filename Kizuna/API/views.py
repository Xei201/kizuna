import csv
import logging
import datetime
import uuid

from django.http import HttpResponse
from django.views.generic import TemplateView
from rest_framework import generics, status
from urllib.parse import urlencode
from django.shortcuts import render, get_object_or_404
from django.utils.encoding import force_str
from django.views import generic
from django.views.generic.edit import UpdateView, FormView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response

from .core.exceptions import NoModelFoundException, NoCorrectPermission
from .core.export_csv import ExportCSV
from .core.import_logic import ImportGetcorseValidation, ImportGetcourseValidationPK, ConvertedTestCSV
from .forms import QuantityWebroom, SettingForm, DownLoadedFileForm, CorrectFieldsForm, DownLoadedTestFileForm
from .core.request_service import RequestBizon, RequestGetcorse
from .models import WebroomTransaction, ViewersImport, TokenImport, FileImportGetcourse
from .core.serializers import WebroomSerializer
from .core.permissions import SuccessToken

logger = logging.getLogger(__name__)


class InitialImportAPIView(generics.CreateAPIView):
    """API отвечающая за импорт людей из Bizon в Getcourse"""

    model = WebroomTransaction
    serializer_class = WebroomSerializer
    permission_classes = (SuccessToken, )

    def perform_create(self, serializer):
        user_id = TokenImport.objects.get(token=self.request.GET.get('token')).user
        logger.info(f"Initiation API import to Getcourse viewers from API to Bizon "
                    f"request {self.request}")
        serializer.save(user_id=user_id)

    def create(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        webroom = serializer.data["webinarId"]
        export = RequestBizon(self.request)
        if export.export_viwers(webroom):
            imp = ImportGetcorseValidation(self.request)
            imp.start_import_to_getcourse_api(webroom)
        else:
            logger.warning(f"Fallen API import to Getcourse viewers from API to Bizon "
                        f"request {self.request}")
        return Response(serializer.data, status=status.HTTP_200_OK)


@login_required
@permission_required("API.can_request", raise_exception=True)
def index(request):
    """Представление выводящее общие данные статистики"""

    webroom_all = WebroomTransaction.objects.all().count()
    webroom_quantity = WebroomTransaction.objects.filter(user_id=request.user).count()
    return render(request, "index.html", context={
        "webroom_all": webroom_all,
        "webroom_quantity": webroom_quantity,
    })


class WebroomList(PermissionRequiredMixin, generic.ListView):
    """Список вебинаров импортированных юзером"""

    model = WebroomTransaction
    context_object_name = "webrooms"
    template_name = 'webroom/list_webroom.html'
    paginate_by = 10
    permission_required = ("API.can_request",)

    def get_queryset(self):
        user_id = self.request.user
        return WebroomTransaction.objects.filter(user_id=user_id).order_by('create')


class WebroomDetail(PermissionRequiredMixin, generic.DetailView):
    """Данные по конкретному импорту пользователей"""

    template_name = "webroom/detail_webroom.html"
    context_object_name = "webroom"
    permission_required = ("API.can_request",)

    def get_object(self):
        return get_object_or_404(WebroomTransaction, pk=self.kwargs.get('pk'))


class ImportViewersListView(PermissionRequiredMixin, generic.ListView):
    """Ведётся повторный импорт на геткурс, после выводится
    список пользователей """

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
        imp = RequestGetcorse(self.request)
        return imp.import_viewers(webinarId)


class ExportViewersCSV(PermissionRequiredMixin, ExportCSV):
    """Генерирует CSV файл с списком импортированных людей"""

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


class HandImportView(PermissionRequiredMixin, FormView):
    """Форма для получения параметров запроса списка вебинаров"""

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


class ExportWebroomListView(PermissionRequiredMixin, generic.ListView):
    """Список вебнаров в рамках ручного импорта"""

    model = None
    template_name = 'webroom/response_webroom.html'
    context_object_name = "list_webinar"
    permission_required = ("API.can_request",)
    paginate_by = 10

    def get_queryset(self):
        webroom_quantity = int(self.kwargs.get("wq"))
        export = RequestBizon(self.request)
        list_webinar = export.get_web_list(webroom_quantity)
        return list_webinar


class HandImportViewersListView(ImportViewersListView):
    """Список пользователей импортированных в ручном режиме"""

    def _get_webinar_id(self):
        webinarId = self.request.GET.get('webinarId')
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


class SettingsUpdateView(PermissionRequiredMixin, UpdateView):
    """Страница установки token внешних сервисов"""

    model = TokenImport
    form_class = SettingForm
    permission_required = ("API.can_request",)
    template_name = "setting/setting_form.html"
    success_url = reverse_lazy("setting")

    # Получение объекта через авторизованого юзера
    def get_object(self, queryset=None):
        return TokenImport.objects.get(user=self.request.user)


class SettingsDelayView(PermissionRequiredMixin, generic.DetailView):
    """Представление токенов юзера"""

    model = TokenImport
    fields = ["token_gk", "name_gk", "token_bizon"]
    permission_required = ("API.can_request",)
    template_name = "setting/setting_delay.html"
    context_object_name = "user_token"

    # Получение объекта через авторизованого юзера
    def get_object(self, queryset=None):
        return TokenImport.objects.get(user=self.request.user)


class DownloadedFileImportGetcourse(PermissionRequiredMixin, generic.CreateView):
    """Форма загрузки CSV для импорта пользователей на Getcourse"""

    permission_required = ("API.can_request",)
    template_name = 'import_gk/downloaded_file.html'
    form_class = DownLoadedFileForm
    success_url = reverse_lazy('correct-field-getcourse')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class CorrectFileFieldImportGetcourse(PermissionRequiredMixin, FormView):
    """Пользователь выбирает соотношение полей в последнем загруженном CSV файле и полей модели импорта"""

    permission_required = ("API.can_request",)
    template_name = 'import_gk/correct_field_params.html'
    form_class = CorrectFieldsForm
    success_url = reverse_lazy('success-import-getcourse')
    import_validation_class = ImportGetcorseValidation

    def get(self, request, *args, **kwargs):
        """Добавление в форму параметров choices из файла CSV"""

        context_data = self.get_context_data()
        self.get_coices_for_form(request, context_data["form"], **kwargs)
        return self.render_to_response(context_data)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        self.get_coices_for_form(request, form, **kwargs)
        if form.is_valid():
            field_position_dict = form.cleaned_data
            user = request.user
            file_data = FileImportGetcourse.objects.filter(user=user).last()
            webroom = file_data.group_user + str(file_data.date_load)
            group = file_data.group_user
            imp = self.get_import_validation_class(request=request, **kwargs)
            if imp.start_upload_viewers_csv_to_bd(field_position_dict):
                imp.start_import_to_getcorse_csv(webroom, group=group)
                return self.form_valid(form)

        return self.form_invalid(form)

    def get_coices_for_form(self, request, form, **kwargs):
        imp = self.get_import_validation_class(request, **kwargs)
        list_choices_tuple = imp.get_choices_field()
        form.fields['email'].choices = list_choices_tuple
        form.fields['name'].choices = list_choices_tuple
        form.fields['phone'].choices = list_choices_tuple

    def get_import_validation_class(self, request, **kwargs):
        """Return the import validation class to use."""
        return self.import_validation_class(request, **kwargs)


class SuccessImportGetcourse(PermissionRequiredMixin, TemplateView):
    """Страница после завершения импорта на Getcourse"""

    permission_required = ("API.can_request",)
    template_name = 'import_gk/success_import.html'


class CSVFileImportList(PermissionRequiredMixin, generic.ListView):
    """Список файлов CSV импортированных юзером"""

    model = WebroomTransaction
    context_object_name = "files"
    template_name = 'import_gk/list_csv_file.html'
    paginate_by = 10
    permission_required = ("API.can_request",)

    def get_queryset(self):
        user_id = self.request.user
        return FileImportGetcourse.objects.filter(user_id=user_id)


class ReimportFileGetcorse(CorrectFileFieldImportGetcourse):
    """Пользователь выбирает соотношение полей в выбранном CSV файле и полей модели импорта"""

    import_validation_class = ImportGetcourseValidationPK


class Test_upload_data_FormView(PermissionRequiredMixin, FormView):
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

            converted_data = ConvertedTestCSV.convert_data(file)
            wr.writerows(converted_data)
            return response












