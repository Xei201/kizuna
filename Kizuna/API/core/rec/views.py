from urllib.parse import urlencode
from django.shortcuts import render, get_object_or_404
from django.utils.encoding import force_str
from django.views import generic
from django.views.generic.edit import UpdateView, DeleteView, FormView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils.translation import gettext_lazy as _

from API.core.exceptions import NoModelFoundException, NoCorrectPermissionToken
from API.core.export_csv import ExportCSV
from API.forms import QuantityWebroom, SettingForm

import datetime

from API.models import WebroomTransaction, ViewersImport, TokenImport
from API.core.request_service import RequestBizon, RequestGetcorse


@permission_required("catalog.can_request")
def index(request):
    """Главная страница выводящая общие данные статистики"""

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
    permission_required = ("catalog.can_request", )

    def get_queryset(self):
        return WebroomTransaction.objects.filter(user_id=self.request.user).order_by('create')


class WebroomDetail(PermissionRequiredMixin, generic.DetailView):
    """Даныые по конкретному импорту вебинара"""

    object = WebroomTransaction
    template_name = "webroom/detail_webroom.html"
    context_object_name = "webroom"
    permission_required = ("catalog.can_request", )
    # queryset = WebroomTransaction.objects.filter(live=True)

    def get_object(self, queryset=None):
        return get_object_or_404(WebroomTransaction, pk=(self.kwargs.get('pk')+1))


class ImportViewersListView(PermissionRequiredMixin, generic.ListView):
    """Ведётся повторный импорт на геткурс, после выводится
    список пользователей """

    model = ViewersImport
    template_name = 'webroom/list_viewers.html'
    context_object_name = "list_viewers"
    permission_required = ("catalog.can_request",)
    paginate_by = 20

    def get_queryset(self):
        webinarId = self._get_webinar_id()
        self._import_gk(webinarId)
        webroom_id = WebroomTransaction.objects.get(webinarId=webinarId).id
        return ViewersImport.objects.filter(webroom_id=webroom_id)

    def _get_webinar_id(self):
        return WebroomTransaction.objects.get(id=self.kwargs.get('pk')).webinarId

    def _import_gk(self, webinarId):
        imp = RequestGetcorse(self.request)
        imp.import_viewers(webinarId)


class ExportViewersCSV(PermissionRequiredMixin, ExportCSV):
    """Генерирует CSV файл с списком импортированных людей"""

    model = ViewersImport
    field_names = ["name", "email", "phone", "view", "buttons", "banners", "create"]
    add_col_names = True
    col_names = ["Имя", "Почта", "Телефон", "Время", "Кнопки", "Баннеры", "Создан"]
    permission_required = ("catalog.can_request",)

    def get_queryset(self):
        user = self.request.user
        pk = self.kwargs.get('pk')
        webroom = WebroomTransaction.objects.get(pk=pk)
        if WebroomTransaction.objects.get(pk=pk).user_id != user:
            exception_msg = "No permission"
            raise NoCorrectPermissionToken(_(exception_msg))
        queryset = webroom.viewersimport_set.all()
        if queryset.exists():
            return queryset
        else:
            exception_msg = "No model to get queryset from. Either provide " \
                            "a model or override get_queryset method."
            raise NoModelFoundException(_(exception_msg))

    def get_filename(self):
        if self.filename is not None:
            return self.filename
        if self.model is not None:
            pk = self.kwargs.get('pk')
            model_name = WebroomTransaction.objects.get(pk=pk).__str__().lower()
            self.filename = force_str(model_name + '_list.csv')
        else:
            exception_msg = "No model to generate filename. Either provide " \
                            "model or filename or override get_filename " \
                            "method."
            raise NoModelFoundException(_(exception_msg))
        return self.filename


class HandImportView(PermissionRequiredMixin, FormView):
    """Форма для получения параметров запроса списка вебинаров"""

    template_name = 'webroom/get_webroom.html'
    form_class = QuantityWebroom
    permission_required = ("catalog.can_request",)

    def form_valid(self, form):
        self.form = form
        return super().form_valid(form)

    def get_success_url(self):
        wq = self.form.cleaned_data['quantity_webroom']
        params = {"date_min": self.form.cleaned_data["date_min"],
                  "date_max": self.form.cleaned_data["date_max"]}
        return (reverse("get-bizon-web", args=[str(wq)]) + '?' + urlencode(params))

    def get_initial(self):
        initial = super().get_initial()
        initial["date_min"] = datetime.date.today() - datetime.timedelta(weeks=4)
        initial["date_max"] = datetime.date.today()
        return initial


class ExportWebroomListView(PermissionRequiredMixin, generic.ListView):
    """Список вебнаров в рамках ручного импорта"""

    model = None
    template_name = 'webroom/response_webroom.html'
    context_object_name = "list_webinar"
    permission_required = ("catalog.can_request",)
    paginate_by = 10

    def get_queryset(self):
        webroom_quantity = abs(int(self.kwargs.get("wq")))
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

    def _import_gk(self, webinarId):
        export = RequestBizon(self.request)
        export.export_viwers(webinarId)
        super()._import_gk(webinarId)


class SettingsUpdateView(PermissionRequiredMixin, UpdateView):
    """Страница установки token внешних сервисов"""

    model = TokenImport
    form_class = SettingForm
    permission_required = ("catalog.can_request",)
    template_name = "setting/setting_form.html"
    success_url = reverse_lazy("setting")

    # Получение объекта через авторизованого юзера
    def get_object(self, queryset=None):
        return TokenImport.objects.get(user=self.request.user)


class SettingsDelayView(PermissionRequiredMixin, DeleteView):
    """Представление токенов юзера"""

    model = TokenImport
    fields = ["token_gk", "name_gk", "token_bizon"]
    permission_required = ("catalog.can_request",)
    template_name = "setting/setting_delay.html"
    context_object_name = "user_token"

    # Получение объекта через авторизованого юзера
    def get_object(self, queryset=None):
        return TokenImport.objects.get(user=self.request.user)







