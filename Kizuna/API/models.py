import uuid

from django.db import models
from django.contrib.auth.models import User
import uuid


def get_default_field_token():
    return uuid.uuid4()


class WebroomTransaction(models.Model):
    event = models.CharField(max_length=200)
    roomid = models.CharField(max_length=200)
    webinarId = models.CharField(max_length=200)
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    start_upload = models.BooleanField(default=False)
    result_upload = models.BooleanField(default=False)
    user_id = models.ForeignKey(User,
                                on_delete=models.SET_NULL,
                                default=None,
                                null=True)

    class META:
        ordering = ["create"]

    def __str__(self):
        return self.webinarId


class TokenImport(models.Model):
    token = models.UUIDField(primary_key=True,
                             default=get_default_field_token)
    token_gk = models.CharField(max_length=100, default=None, null=True)
    token_bizon = models.CharField(max_length=100, default=None, null=True)
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ["create"]

    def __str__(self):
        return str(self.token)


class ViewersImport(models.Model):
    email = models.EmailField(max_length=200)
    phone = models.CharField(max_length=200)
    view = models.CharField(max_length=200)
    buttons = models.CharField(max_length=200, null=True)
    banners = models.CharField(max_length=200, null=True)
    create = models.DateTimeField(auto_now_add=True)
    import_to_gk = models.BooleanField(default=False)
    webroom = models.ForeignKey(WebroomTransaction,
                                on_delete=models.CASCADE,
                                null=True)

    class Meta:
        ordering = ["create"]

    def __str__(self):
        return self.email





