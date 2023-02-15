from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator


class QuantityWebroom(forms.Form):
    quantity_webroom = forms.IntegerField(label="Количество вебинаров", initial=1,
                                          help_text="в диапазоне от 1 до 100",
                                          validators=[MinValueValidator(1), MaxValueValidator(100)])
