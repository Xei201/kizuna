from django.http import HttpResponse
from rest_framework import generics

from .request_servise import RequestBizon, RequestGetcorse
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

    def create(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        webinar_id = serializer.data["webinarId"]
        export = RequestBizon(self.request)
        export.export_viwers(webinar_id)
        imp = RequestGetcorse(self.request)
        imp.import_viewers(webinar_id)




