from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse

from API.models import TokenImport


class SettingViewTest(TestCase):

    def setUp(self):
        # Создание тестовых пользователей
        user1 = User.objects.create_user(username="test1", password="12345")
        user1.save()
        user2 = User.objects.create_user(username="test2", password="12345")
        user2.save()
        # Выдача тестовому пользователю прав доступа и тестовых токенов
        permission = Permission.objects.get(name='Has request to GK, Bizon')
        user2.user_permissions.add(permission)
        user2.save()
        TokenImport.objects.create(
            user=user2,
            token_gk="123456789",
            token_bizon="qwerrty",
            name_gk="test"
        )

    def test_redirect_if_user_has_no_corrected_permission_settings(self):
        Login = self.client.login(username="test1", password="12345")
        resp = self.client.get(reverse("setting-delay"))
        self.assertEqual(resp.status_code, 403)
        resp = self.client.get(reverse("setting"))
        self.assertEqual(resp.status_code, 403)

    def test_open_sours_if_user_has_permission_setting(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse("setting-delay"))
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(reverse("setting"))
        self.assertEqual(resp.status_code, 200)

    def test_template_setting(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse("setting-delay"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "setting/setting_delay.html")

        resp = self.client.get(reverse("setting"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "setting/setting_form.html")

    def test_form_initial_data_update_setting(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse("setting"))
        user_test = User.objects.get(id=2)
        token_data = TokenImport.objects.get(user=user_test)
        name_gk = token_data.name_gk
        tok_biz = token_data.token_bizon
        tok_gk = token_data.token_getcourse
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['form'].initial['name_gk'], name_gk)
        self.assertEqual(resp.context['form'].initial['token_gk'], tok_biz)
        self.assertEqual(resp.context['form'].initial['token_bizon'], tok_gk)

    def test_form_initial_data_delay_setting(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse("setting"))
        user_test = User.objects.get(id=2)
        token_data = TokenImport.objects.get(user=user_test)
        name_gk = token_data.name_gk
        tok_biz = token_data.token_bizon
        tok_gk = token_data.token_getcourse
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['name_gk'], name_gk)
        self.assertEqual(resp.context['token_bizon'], tok_biz)
        self.assertEqual(resp.context['token_gk'], tok_gk)


class IndexViewTest(TestCase):

    def setUp(self):
        # Создание тестовых пользователей
        user1 = User.objects.create_user(username="test1", password="12345")
        user1.save()
        user2 = User.objects.create_user(username="test2", password="12345")
        user2.save()
        # Выдача тестовому пользователю прав доступа и тестовых токенов
        permission = Permission.objects.get(name='Has request to GK, Bizon')
        user2.user_permissions.add(permission)
        user2.save()
        TokenImport.objects.create(
            user=user2,
            token_gk="123456789",
            token_bizon="qwerrty",
            name_gk="test"
        )

    def test_redirect_if_user_has_no_corrected_permission_index(self):
        Login = self.client.login(username="test1", password="12345")
        resp = self.client.get(reverse("index"))
        self.assertEqual(resp.status_code, 403)

    def test_open_sours_if_user_has_permission_index(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse("index"))
        self.assertEqual(resp.status_code, 200)

    def test_template_index(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse("index"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "index.html")




