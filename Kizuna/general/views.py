from django.shortcuts import render

from django.contrib.auth.decorators import login_required, permission_required
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.urls import reverse

from API.models import WebroomTransaction, TokenImport, ViewersImport
from API.request_servise import get_bizon_web_list
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

            return HttpResponseRedirect(reverse("get-bizon-web", args=[str(wq)]))
    else:
        form = QuantityWebroom()
    return render(request, 'webroom/get_webroom.html', {"form": form})


def get_bizon_web(request, wq):
    webroom_quantity = int(wq)
    list_webinar = get_bizon_web_list(request, webroom_quantity)
    return render(request, 'webroom/response_webroom.html', context={"list_webinar": list_webinar})
