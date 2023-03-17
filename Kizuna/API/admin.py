from django.contrib import admin
from .models import WebroomTransaction, TokenImport, ViewersImport, FileImportGetcourse


class ViewersInline(admin.TabularInline):
    model = ViewersImport


@admin.register(WebroomTransaction)
class WebrummAdmin(admin.ModelAdmin):
    list_display = ("event", "roomid", "webinarId", "create", "update", "start_upload", "result_upload", "user_id")
    list_filter = ("create", "roomid")
    inlines = [ViewersInline]


@admin.register(TokenImport)
class TokenAdmin(admin.ModelAdmin):
    list_display = ("user", "create", "token", "token_gk")
    list_filter = ("user", "create")


@admin.register(ViewersImport)
class ViewsAdmin(admin.ModelAdmin):
    list_display = ("email", "phone", "view", "create", "import_to_gk")
    list_filter = ("email", "phone", "view", "create", "import_to_gk")


@admin.register(FileImportGetcourse)
class ViewsAdmin(admin.ModelAdmin):
    list_display = ("file", "user", "group_user", "date_load")
    list_filter = ("date_load", )

