from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _


class QuantityWebroom(forms.Form):
    quantity_webroom = forms.IntegerField(label="Количество вебинаров", initial=1,
                                          help_text="в диапазоне от 1 до 100",
                                          validators=[MinValueValidator(1), MaxValueValidator(100)])
    date_min = forms.DateField(help_text="Стартовая дата", required=False)
    date_max = forms.DateField(help_text="Конечная дата", required=False)

    def clean_date_max(self):
        date_min = self.cleaned_data["date_min"]
        date_max = self.cleaned_data["date_max"]

        if not date_max:
            return date_max

        if date_min > date_max:
            raise ValidationError(_("Конечная дата должна быть больше стартовой"))

        return date_max