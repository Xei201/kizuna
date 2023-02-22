from urllib.parse import urlencode
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.encoding import force_str
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils.translation import gettext_lazy as _


from .exceptions import NoModelFoundException, NoCorrectPermissionToken
from .export_csv import ExportCSV
from .forms import QuantityWebroom

import datetime

from API.models import WebroomTransaction, ViewersImport
from API.request_servise import RequestBizon, RequestGetcorse


@permission_required("catalog.can_request")
def index(request):
    webroom_all = WebroomTransaction.objects.all().count()
    webroom_quantity = WebroomTransaction.objects.filter(user_id=request.user).count()
    return render(request, "index.html", context={
        "webroom_all": webroom_all,
        "webroom_quantity": webroom_quantity,
    })


class WebroomList(generic.ListView):
    model = WebroomTransaction
    context_object_name = "webrooms"
    template_name = 'webroom/list_webroom.html'
    paginate_by = 10
    permission_required = ("catalog.can_request", )

    def get_queryset(self):
        return WebroomTransaction.objects.filter(user_id=self.request.user).order_by('create')


class WebroomDetail(generic.DetailView):
    model = WebroomTransaction
    template_name = "webroom/detail_webroom.html"
    context_object_name = "webroom"
    permission_required = ("catalog.can_request", )


class ImportViewersListView(PermissionRequiredMixin, generic.ListView):
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


class ExportViewersCSV(PermissionRequiredMixin ,ExportCSV):
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

    def get(self, request, pk):
        return self._create_csv()


@permission_required("catalog.can_request")
def hand_import(request):
    if request.method == "POST":
        form = QuantityWebroom(request.POST)

        if form.is_valid():
            wq = form.cleaned_data['quantity_webroom']
            params = {"date_min": form.cleaned_data["date_min"],
                      "date_max": form.cleaned_data["date_max"]}

            return HttpResponseRedirect(reverse("get-bizon-web", args=[str(wq)]) + '?' + urlencode(params))
    else:
        date_min = datetime.date.today() - datetime.timedelta(weeks=4)
        date_max = datetime.date.today()
        form = QuantityWebroom(initial={"date_min": date_min, "date_max": date_max})
    return render(request, 'webroom/get_webroom.html', {"form": form})


class ExportWebroomListView(PermissionRequiredMixin, generic.ListView):
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
