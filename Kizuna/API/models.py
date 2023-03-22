import os.path

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import uuid

from Kizuna import settings


def get_default_field_token():
    return uuid.uuid4()


class WebroomTransaction(models.Model):
    """Модель хранящая данные о переданных вебинарах и их статусы"""

    event = models.CharField(max_length=200, verbose_name='Type_event')
    roomid = models.CharField(max_length=200, verbose_name='ID_number_webinar_room')
    webinarId = models.CharField(max_length=200, verbose_name='ID_webinar_event')
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    start_upload = models.BooleanField(default=False)
    result_upload = models.BooleanField(default=False)
    user_id = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        default=None,
        null=True
    )

    class META:
        ordering = ["create"]

    def get_absolute_url(self):
        return reverse('detail-webroom', args=[str(self.id)])

    def get_import_url(self):
        return reverse('reimport-webroom', args=[str(self.id)])

    def get_export_csv_url(self):
        return reverse('upload-webroom', args=[str(self.id)])

    def __str__(self):
        return self.webinarId


class TokenImport(models.Model):
    """Модель хранящая токены от сервисов пользователей"""

    token = models.UUIDField(primary_key=True,
                             default=get_default_field_token)
    token_gk = models.CharField(
        max_length=260,
        default=None,
        null=True
    )
    name_gk = models.CharField(
        max_length=200,
        default=None,
        null=True
    )
    token_bizon = models.CharField(
        max_length=2600,
        default=None,
        null=True
    )
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    class Meta:
        permissions = (("can_request", "Has request to GK, Bizon"),)
        ordering = ["create"]

    def __str__(self):
        return str(self.user)


class ViewersImport(models.Model):
    """Модель хранящая данные переданных пользователей"""

    name = models.CharField(
        max_length=200,
        default='Not found'
    )
    email = models.EmailField(max_length=200)
    phone = models.CharField(max_length=200)
    view = models.CharField(max_length=200)
    buttons = models.CharField(
        max_length=200,
        null=True
    )
    banners = models.CharField(
        max_length=200,
        null=True
    )
    create = models.DateTimeField(auto_now_add=True)
    import_to_gk = models.BooleanField(default=False)
    webroom = models.ForeignKey(
        WebroomTransaction,
        on_delete=models.CASCADE,
        null=True
    )

    class Meta:
        ordering = ["create"]

    def __str__(self):
        return self.email


class FileImportGetcourse(models.Model):
    file = models.FileField(upload_to=settings.DIRECTORY_FROM_FILE_IMPORT)
    date_load = models.DateTimeField(auto_now_add=True)
    group_user = models.CharField(max_length=200, default=None)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        default=None,
        null=True
    )

    class Meta:
        ordering = ["date_load"]

    def __str__(self):
        return os.path.basename(self.file.name)

    def get_import_url(self):
        return reverse('reimport-getcourse', args=[str(self.id)])




