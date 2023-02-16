from urllib.parse import urlencode
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
import datetime

from API.models import WebroomTransaction, TokenImport, ViewersImport
from API.request_servise import get_bizon_web_list, export_bizon, import_gk
from .forms import QuantityWebroom


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

    def get_queryset(self):
        return WebroomTransaction.objects.filter(user_id=self.request.user).order_by('create')


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


def get_bizon_web(request, wq):
    webroom_quantity = abs(int(wq))
    list_webinar = get_bizon_web_list(request, webroom_quantity)
    return render(request, 'webroom/response_webroom.html', context={"list_webinar": list_webinar})


def hand_import_start(request):
    webinarId = request.GET.get('webinarId')
    if not WebroomTransaction.objects.filter(webinarId=webinarId).exists():
        webroom = WebroomTransaction()
        webroom.event = request.GET.get('event')
        webroom.roomid = request.GET.get('roomid')
        webroom.webinarId = webinarId
        webroom.user_id = request.user
        webroom.save()
    export_bizon(webinarId, request)
    import_gk(webinarId, request)
    webroom_id = WebroomTransaction.objects.get(webinarId=webinarId).id
    list_viewers = ViewersImport.objects.filter(webroom_id=webroom_id)
    return render(request, 'webroom/list_viewers.html', context={"list_viewers": list_viewers})
