from django.http import HttpResponse
from rest_framework import generics

from . import request_servise
from .models import WebroomTransaction, ViewersImport, TokenImport
from .serializers import WebroomSerializer
from .permissions import SuccessToken


class InitialImportAPIView(generics.CreateAPIView):
    model = WebroomTransaction
    serializer_class = WebroomSerializer
    permission_classes = (SuccessToken, )

    def perform_create(self, serializer):
        user_id = TokenImport.objects.get(token=self.request.GET.get('token')).user
        serializer.save(user_id=user_id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        webinar_id = serializer.data["webinarId"]
        request_servise.export_bizon(webinar_id, request)
        request_servise.import_gk(webinar_id, request)
        return HttpResponse("<h1>Successfully created</h1>")




