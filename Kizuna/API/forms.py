import re

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from API.core.import_logic import ConvertedTestCSV
from API.models import TokenImport, FileImportGetcourse
from API.core.request_service import RequestBizon, RequestGetcorse
from Kizuna import settings


class QuantityWebroom(forms.Form):
    """Форма для ввода данных по выборке вебинаров"""

    quantity_webroom = forms.IntegerField(label="Количество вебинаров", initial=1,
                                          help_text="в диапазоне от 1 до 100",
                                          validators=[MinValueValidator(1), MaxValueValidator(100)])
    date_min = forms.DateField(label="Стартовая дата", help_text="Стартовая дата", required=False)
    date_max = forms.DateField(label="Конечная дата", help_text="Конечная дата", required=False)

    def clean_date_max(self):
        date_min = self.cleaned_data["date_min"]
        date_max = self.cleaned_data["date_max"]

        if not date_max:
            return date_max

        if date_min > date_max:
            raise ValidationError(_("Конечная дата должна быть больше стартовой"))

        return date_max


class SettingForm(ModelForm):
    """Форма внесение токенов внешних сервисов с проверкой их валидности"""

    class Meta:
        model = TokenImport
        fields = ["name_gk", "token_gk", "token_bizon"]

    def clean_name_gk(self) -> str:
        """Проверка валидности имени акканта Getcourse"""

        name_gk = self.cleaned_data["name_gk"]
        self.name_gk = name_gk
        if len(name_gk) < 3:
            raise ValidationError(_("Название Вашего аккаунта должно содержать "
                                    "больше 2 символов"))
        if self._valid_value(name_gk):
            raise ValidationError(_("Название Вашего аккаунта должно содержать "
                                    "и состоять из букв, цифр, - и _"))

        return name_gk

    def clean_token_bizon(self) -> str:
        token = self.cleaned_data["token_bizon"]
        if self._valid_value(token):
            raise ValidationError(_("Token должен содержать цифры, буквы, - и _"))

        if not RequestBizon.test_token_bizon(token):
            raise ValidationError(_("Bizon не подтвердил валидность Вашего token"))

        return token

    def clean_token_gk(self) -> str:
        token = self.cleaned_data["token_gk"]
        name_gk = self.name_gk
        if self._valid_value(token):
            raise ValidationError(_("Token должен содержать цифры, буквы, - и _"))

        if not RequestGetcorse.test_token_gk(token, name_gk):
            raise ValidationError(_("Getcourse не подтвердил валидность Вашего token"))

        return token

    def _valid_value(self, name: str) -> bool:
        return re.fullmatch(r'[0-9a-zA-Z_-]+', name) is None


class DownLoadedFileForm(ModelForm):
    """Отвечает за загрузку CSV файла с контактами студентов"""

    class Meta:
        model = FileImportGetcourse
        fields = ("file", "group_user")

    def clean_file(self) -> str:
        file_name = self.cleaned_data["file"].name
        if not file_name.endswith(".csv"):
            raise ValidationError(_("Тип файла должен быть CSV"))

        return self.cleaned_data["file"]


class CorrectFieldsForm(forms.Form):
    """Форма уточнения выборки столбивков файла CSV для имяпорта в GC"""

    email = forms.ChoiceField()
    name = forms.ChoiceField()
    phone = forms.ChoiceField()


class DownLoadedTestFileForm(forms.Form):
    """Форма для загрузки файла конвертируемого тестирования"""

    file = forms.FileField(label="Ваш файл", help_text="Загрузите файл в формате CSV",)

    def clean_file(self) -> str:
        file = self.cleaned_data["file"]
        if not file.name.endswith(".csv"):
            raise ValidationError(_("Тип файла должен быть CSV"))

        return file
