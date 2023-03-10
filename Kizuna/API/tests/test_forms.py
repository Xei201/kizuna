import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from API.forms import QuantityWebroom, SettingForm
from Kizuna import settings


class QuantityWebroomTest(TestCase):
    """Test form QuantityWebroom"""

    def test_webroom_form_date_field_params(self):
        form = QuantityWebroom()
        self.assertTrue(form.fields['quantity_webroom'].label == 'Количество вебинаров')
        self.assertTrue(form.fields['quantity_webroom'].initial == 1)
        self.assertTrue(form.fields['quantity_webroom'].help_text == "в диапазоне от 1 до 100")
        self.assertTrue(form.fields['date_min'].help_text == "Стартовая дата")
        self.assertTrue(form.fields['date_max'].help_text == "Конечная дата")

    def test_webroom_form_field_quantity_uncorrect_params(self):
        date_max = datetime.date.today()
        date_min = date_max - datetime.timedelta(weeks=4)
        quan = 1000
        form_data = {"quantity_webroom": quan,
                     "date_min": date_min,
                     "date_max": date_max}
        form = QuantityWebroom(data=form_data)
        self.assertFalse(form.is_valid())
        quan = -2
        form = QuantityWebroom(data=form_data)
        self.assertFalse(form.is_valid())

    def test_webroom_form_fields_correct_params(self):
        date_max = datetime.date.today()
        date_min = date_max - datetime.timedelta(weeks=4)
        quan = 50
        form_data = {"quantity_webroom": quan,
                     "date_min": date_min,
                     "date_max": date_max}
        form = QuantityWebroom(data=form_data)
        self.assertTrue(form.is_valid())

    def test_webroom_form_field_date_uncorrect_params(self):
        date_min = datetime.date.today()
        date_max = date_min - datetime.timedelta(weeks=4)
        quan = 50
        form_data = {"quantity_webroom": quan,
                     "date_min": date_min,
                     "date_max": date_max}
        form = QuantityWebroom(data=form_data)
        self.assertFalse(form.is_valid())

    def test_webroom_form_field_date_required_params(self):
        quan = 50
        form_data = {"quantity_webroom": quan,
                     "date_min": "",
                     "date_max": ""}
        form = QuantityWebroom(data=form_data)
        self.assertTrue(form.is_valid())


class SettingFormTest(TestCase):
    """Test form SettingForm"""

    def test_setting_form_date_field_params(self):
        form = SettingForm()
        self.assertIn("name_gk", form.fields)
        self.assertIn("token_gk", form.fields)
        self.assertIn("token_bizon", form.fields)

    def test_setting_form_field_name_gk_uncorrect_params(self):
        token_gk = settings.GETCOURSE_TEST_API
        token_bizon = settings.BIZON_TEST_API
        name_gk = "gg"
        form_data = {"name_gk": name_gk,
                     "token_gk": token_gk,
                     "token_bizon": token_bizon}
        form = SettingForm(data=form_data)
        self.assertFalse(form.is_valid())
        name_gk = 'gg32234;'
        form_data = {"name_gk": name_gk,
                     "token_gk": token_gk,
                     "token_bizon": token_bizon}
        self.assertFalse(form.is_valid())
        name_gk = 'gg32234умуммк'
        form_data = {"name_gk": name_gk,
                     "token_gk": token_gk,
                     "token_bizon": token_bizon}
        self.assertFalse(form.is_valid())

    def test_setting_form_field_name_gk_correct_params(self):
        token_gk = settings.GETCOURSE_TEST_API
        token_bizon = settings.BIZON_TEST_API
        name_gk = "ggevvrev23424324"
        form_data = {"name_gk": name_gk,
                     "token_gk": token_gk,
                     "token_bizon": token_bizon}
        form = SettingForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_setting_form_field_tokens_uncorrect_params(self):
        token_gk = 'evrevrve;&()'
        token_bizon = settings.BIZON_TEST_API
        name_gk = "ggevvrev_-23424324"
        form_data = {"name_gk": name_gk,
                     "token_gk": token_gk,
                     "token_bizon": token_bizon}
        form = SettingForm(data=form_data)
        self.assertFalse(form.is_valid())
        token_gk = settings.GETCOURSE_TEST_API
        token_bizon = 'evrevrve;&()'
        form_data = {"name_gk": name_gk,
                     "token_gk": token_gk,
                     "token_bizon": token_bizon}
        form = SettingForm(data=form_data)
        self.assertFalse(form.is_valid())
