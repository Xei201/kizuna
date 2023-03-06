from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse

from API.models import TokenImport, WebroomTransaction, ViewersImport
from Kizuna import settings


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
            name_gk="test")

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
        tok_gk = token_data.token_gk
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
        tok_gk = token_data.token_gk
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
            name_gk="test")

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


class MyWebroomImportViewTest(TestCase):

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
            name_gk="test")

        # Генерация списка вебинаров юзер 1
        number_of_web = 3
        for it in range(number_of_web):
            WebroomTransaction.objects.create(
                event="webinarEnd",
                roomid=f"24105:user1-{it}",
                webinarId=f"24105:user1-web160{it}-02-15T19:00:{it}",
                user_id=user1)

        # Генерация списка вебинаров юзер 2
        number_of_web = 15
        for it in range(number_of_web):
            WebroomTransaction.objects.create(
                event="webinarEnd",
                roomid=f"24105:user2-{it}",
                webinarId=f"24105:user2-web160{it}-02-15T19:00:{it}",
                user_id=user2)

    def test_redirect_if_user_has_no_corrected_permission_mywebroom(self):
        Login = self.client.login(username="test1", password="12345")
        resp = self.client.get(reverse("my-webroom"))
        self.assertEqual(resp.status_code, 403)

    def test_open_sours_if_user_has_permission_mywebroom(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse("my-webroom"))
        self.assertEqual(resp.status_code, 200)

    def test_template_mywebroom(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse("my-webroom"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "webroom/list_webroom.html")

    def test_pagination_is_ten(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse('my-webroom'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue(len(resp.context['webrooms']) == 10)

    def test_lists_all_webroom_and_return_only_my_web(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse('my-webroom')+'?page=2')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue(len(resp.context['webrooms']) == 5)


class MyWebroomDelayViewTest(TestCase):

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
            name_gk="test")

        # Генерация списка вебинаров юзер 2
        number_of_web = 2
        for it in range(number_of_web):
            WebroomTransaction.objects.create(
                event="webinarEnd",
                roomid=f"24105:user2-{it}",
                webinarId=f"24105:user2-web160{it}-02-15T19:00:{it}",
                user_id=user2)

    def test_redirect_if_user_has_no_corrected_permission_detail_webroom(self):
        Login = self.client.login(username="test1", password="12345")
        resp = self.client.get(reverse("detail-webroom", kwargs={"pk": 1, }))
        self.assertEqual(resp.status_code, 403)

    def test_open_sours_if_user_has_permission_detail_webroom(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse("detail-webroom", kwargs={"pk": 1, }))
        self.assertEqual(resp.status_code, 200)

    def test_template_detail_webroom(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse("detail-webroom", kwargs={"pk": 1, }))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "webroom/detail_webroom.html")

    def test_view_detail_of_number_webroom(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse("detail-webroom", kwargs={"pk": 1, }))
        self.assertEqual(resp.status_code, 200)
        webroom = WebroomTransaction.objects.get(pk=1)
        roomid_web = webroom.roomid
        webinarId_web = webroom.webinarId
        self.assertTrue(resp.context['webroom']["roomid"] == roomid_web)
        self.assertTrue(resp.context['webroom']["webinarId"] == webinarId_web)


class MyWebroomReImportViewTest(TestCase):

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
            token_gk=settings.GETCOURSE_TEST_API,
            token_bizon=settings.BIZON_TEST_API,
            name_gk="test")

        # Вебинар для юзер 2

        number_of_web = 2
        for it in range(number_of_web):
            WebroomTransaction.objects.create(
                event="webinarEnd",
                roomid=f"24105:user2-{it}",
                webinarId=f"24105:user2-web160{it}-02-15T19:00:{it}",
                user_id=user2)

        # Генерация списка зритлей на вебинаре
        number_of_viewers = 50
        viwers_list = []
        for it in range(number_of_viewers):
            webroom = it % 2
            viwers_list.append(ViewersImport(
                name=f"Viwer{it}",
                email=f"vivat{it}@test.ru",
                phone=f"0000000000",
                webroom=webroom))
        ViewersImport.objects.bulk_create(viwers_list)

    def test_redirect_if_user_has_no_corrected_permission_detail_webroom(self):
        Login = self.client.login(username="test1", password="12345")
        resp = self.client.get(reverse("reimport-webroom", kwargs={"pk": 1, }))
        self.assertEqual(resp.status_code, 403)

    def test_open_sours_if_user_has_permission_detail_webroom(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse("reimport-webroom", kwargs={"pk": 1, }))
        self.assertEqual(resp.status_code, 200)

    def test_template_detail_webroom(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse("reimport-webroom", kwargs={"pk": 1, }))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "webroom/list_viewers.html")

    def test_pagination_is_twelve(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse('reimport-webroom'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue(len(resp.context['webrooms']) == 20)

    def test_lists_all_webroom_and_return_only_my_viwers(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse('reimport-webroom')+'?page=2')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue(len(resp.context['webrooms']) == 5)

    def test_correct_import(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse('reimport-webroom')+'?page=2')
        self.assertEqual(resp.status_code, 200)
        viewer = ViewersImport.objects.get(pk=1)
        name_viewer = viewer.name
        email_viewer = viewer.email
        self.assertTrue(resp.context['webrooms'][0]["roomid"] == name_viewer)
        self.assertTrue(resp.context['webrooms'][0]["webinarId"] == email_viewer)




