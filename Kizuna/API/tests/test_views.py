import datetime
import re
from os import path

from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_str

from API.models import TokenImport, WebroomTransaction, ViewersImport, TrackedSessinBizon
from Kizuna import settings


class SettingViewTest(TestCase):
    """Test views SettingsDelayView and SettingsUpdateView"""

    def setUp(self) -> None:
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
        self.assertEqual(resp.context['form'].initial['token_gk'], tok_gk)
        self.assertEqual(resp.context['form'].initial['token_bizon'], tok_biz)

    def test_form_initial_data_delay_setting(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse("setting-delay"))
        user_test = User.objects.get(id=2)
        token_data = TokenImport.objects.get(user=user_test)
        name_getcourse = token_data.name_gk
        tok_biz = token_data.token_bizon
        tok_gk = token_data.token_gk
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["user_token"].name_gk, name_getcourse)
        self.assertEqual(resp.context["user_token"].token_bizon, tok_biz)
        self.assertEqual(resp.context["user_token"].token_gk, tok_gk)


class BizonConnectViewTest(TestCase):
    """Test views SettingsDelayView and SettingsUpdateView"""

    def setUp(self) -> None:
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

    def test_redirect_if_user_has_no_corrected_permission_bizon_connect(self):
        Login = self.client.login(username="test1", password="12345")
        resp = self.client.get(reverse("setting-bizon"))
        self.assertEqual(resp.status_code, 403)

    def test_open_sours_if_user_has_permission_bizon_connect(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse("setting-bizon"))
        self.assertEqual(resp.status_code, 200)

    def test_template_bizon_connect(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse("setting-bizon"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "setting/setting_bizon_webhook.html")

    def test_initial_data_generic_urls(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse("setting-bizon"))
        token = TokenImport.objects.get(user_id=2).token
        url = path.join(settings.URL_SERVER, settings.URL_API_INTEGRATION, ("?token=" + str(token)))
        self.assertTrue('url_api' in resp.context)
        self.assertEquals(resp.context["url_api"], url)


class IndexViewTest(TestCase):
    """Test view def index"""

    def setUp(self) -> None:
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
    """Test view WebroomList"""

    def setUp(self) -> None:
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
                webinarId=f"24105:user1-web160{it}-02-15T19:00:-{it}",
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
        self.assertEqual(len(resp.context['webrooms']), 5)


class MyWebroomDelayViewTest(TestCase):
    """Test view WebroomDetail"""

    def setUp(self) -> None:
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
        self.assertTrue(resp.context['webroom'].roomid == roomid_web)
        self.assertTrue(resp.context['webroom'].webinarId == webinarId_web)


class MyWebroomReImportViewTest(TestCase):
    """Test view ImportViewersListView"""

    def setUp(self) -> None:
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
            pk = it % 2 + 1
            webroom = WebroomTransaction.objects.get(pk=pk)
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
        resp = self.client.get(reverse('reimport-webroom', kwargs={"pk": 1, }))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue(len(resp.context['list_viewers']) == 20)

    def test_lists_all_webroom_and_return_only_my_viwers(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse('reimport-webroom', kwargs={"pk": 1, })+'?page=2')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue(len(resp.context['list_viewers']) == 5)

    def test_correct_import(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse('reimport-webroom', kwargs={"pk": 1, }))
        self.assertEqual(resp.status_code, 200)
        viewer = ViewersImport.objects.get(pk=1)
        name_viewer = viewer.name
        email_viewer = viewer.email
        self.assertEqual(resp.context['list_viewers'][0].name, name_viewer)
        self.assertEqual(resp.context['list_viewers'][0].email, email_viewer)


class ExportViewersCSV(TestCase):
    """Test view ExportViewersCSV"""

    def setUp(self) -> None:
        # Создание тестовых пользователей
        user1 = User.objects.create_user(username="test1", password="12345")
        user1.save()
        user2 = User.objects.create_user(username="test2", password="12345")
        user2.save()
        user3 = User.objects.create_user(username="test3", password="12345")
        user3.save()
        # Выдача тестовому пользователю прав доступа и тестовых токенов
        permission = Permission.objects.get(name='Has request to GK, Bizon')
        user2.user_permissions.add(permission)
        user3.user_permissions.add(permission)
        user2.save()
        user3.save()
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
        number_of_viewers = 10
        viwers_list = []
        for it in range(number_of_viewers):
            pk = it % 2 + 1
            webroom = WebroomTransaction.objects.get(pk=pk)
            viwers_list.append(ViewersImport(
                name=f"Viwer{it}",
                email=f"vivat{it}@test.ru",
                phone=f"0000000000",
                webroom=webroom))
        ViewersImport.objects.bulk_create(viwers_list)

    def test_redirect_if_user_has_no_corrected_permission_export_file_webroom(self):
        Login = self.client.login(username="test1", password="12345")
        resp = self.client.get(reverse("upload-webroom", kwargs={"pk": 1, }))
        self.assertEqual(resp.status_code, 403)

    def test_open_sours_if_user_has_permission_export_file_webroom(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse("upload-webroom", kwargs={"pk": 2, }))
        self.assertEqual(resp.status_code, 200)

    def test_non_existent_session_upload_file(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse("upload-webroom", kwargs={"pk": 1000, }))
        self.assertEqual(resp.status_code, 404)

    def test_upload_file_if_user_not_created_export_webroom(self):
        login = self.client.login(username="test3", password="12345")
        resp = self.client.get(reverse("upload-webroom", kwargs={"pk": 1, }))
        self.assertTrue(resp.status_code != 200)

    def test_params_response_from_success_load_csv(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse("upload-webroom", kwargs={"pk": 2, }))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers['Content-Type'], "text/csv")
        if "Content-Disposition" in resp.headers.keys():
            fname = re.findall("filename=(.+)", resp.headers["Content-Disposition"])[0]
            fname_clear = fname[1:-1]
            model_name = WebroomTransaction.objects.get(pk=2).__str__().lower()
            name_file = force_str(model_name + '_list.csv')
            self.assertEqual(fname_clear, name_file)
        else:
            self.assertTrue(False)


class HandImportViewTest(IndexViewTest):
    """Test view HandImport"""

    def setUp(self) -> None:
        # Создание тестовых пользователей
        user1 = User.objects.create_user(username="test1", password="12345")
        user1.save()
        user2 = User.objects.create_user(username="test2", password="12345")
        user2.save()
        # Выдача тестовому пользователю прав доступа и тестовых токенов
        permission = Permission.objects.get(name='Has request to GK, Bizon')
        user2.user_permissions.add(permission)
        user2.save()

    def test_redirect_if_user_has_no_corrected_permission_hand_import(self):
        Login = self.client.login(username="test1", password="12345")
        resp = self.client.get(reverse("hand-import"))
        self.assertEqual(resp.status_code, 403)

    def test_open_sours_if_user_has_permission_export_hand_import(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse("hand-import"))
        self.assertEqual(resp.status_code, 200)

    def test_template_load_hand_import(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse("hand-import"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "webroom/get_webroom.html")

    def test_correct_initial_data_form_field_hand_import(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse("hand-import"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['form'].initial['quantity_webroom'], 1)
        date_past = datetime.date.today() - datetime.timedelta(weeks=4)
        date_today = datetime.date.today()
        self.assertEqual(resp.context['form'].initial['date_min'], date_past)
        self.assertEqual(resp.context['form'].initial['date_max'], date_today)

    def test_correct_validation_field_quantity_hand_import(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse("hand-import"))
        self.assertEqual(resp.status_code, 200)

        non_correct_quantity = 101
        resp = self.client.post(reverse("hand-import"), {"quantity_webroom": non_correct_quantity})
        self.assertFormError(resp, "form", "quantity_webroom", "Ensure this value is less than or equal to 100.")

        non_correct_quantity = 0
        resp = self.client.post(reverse("hand-import"), {"quantity_webroom": non_correct_quantity})
        self.assertFormError(resp, "form", "quantity_webroom", "Ensure this value is greater than or equal to 1.")

    def test_correct_validation_field_date_hand_import(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse("hand-import"))
        self.assertEqual(resp.status_code, 200)
        non_correct_date = datetime.date.today() + datetime.timedelta(weeks=4)
        date_today = datetime.date.today()

        resp = self.client.post(reverse("hand-import"),
                                {"quantity_webroom": 1,
                                 "date_min": non_correct_date,
                                 "date_max": date_today})
        self.assertFormError(resp, "form", "date_max", "Конечная дата должна быть больше стартовой")


class ExportWebroomListTest(TestCase):
    """Test view ExportWebroomListView"""

    def setUp(self) -> None:
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
        number_of_web = 18
        list_web = []
        for it in range(number_of_web):
            list_web.append(WebroomTransaction(
                event="webinarEnd",
                roomid=f"24105:user2-{it}",
                webinarId=f"24105:user2-web160{it}-02-15T19:00:{it}",
                user_id=user2))
        WebroomTransaction.objects.bulk_create(list_web)

    def test_redirect_if_user_has_no_corrected_permission_get_bizon_web(self):
        Login = self.client.login(username="test1", password="12345")
        resp = self.client.get(reverse('get-bizon-web', kwargs={"wq": 18, }))
        self.assertEqual(resp.status_code, 403)

    def test_open_sours_if_user_has_permission_export_get_bizon_web(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse('get-bizon-web', kwargs={"wq": 18, }))
        self.assertEqual(resp.status_code, 200)

    def test_template_load_get_bizon_web(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse('get-bizon-web', kwargs={"wq": 18, }))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "webroom/response_webroom.html")

    def test_pagination_is_ten(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse('get-bizon-web', kwargs={"wq": 18, }))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue(len(resp.context['list_webinar']) == 10)

    def test_lists_all_webroom(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse('get-bizon-web', kwargs={"wq": 18, })+'?page=2')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue(len(resp.context['list_webinar']) == 8)


class HandImportViewersListTest(TestCase):
    """Test view HandImportViewersListView"""
    test_data_request = "?webinarId=24105:user2-web1600-02-15T19:00:0&event=webinarEnd"

    def setUp(self) -> None:
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
            pk = it % 2 + 1
            webroom = WebroomTransaction.objects.get(pk=pk)
            viwers_list.append(ViewersImport(
                name=f"Viwer{it}",
                email=f"vivat{it}@test.ru",
                phone=f"0000000000",
                webroom=webroom))
        ViewersImport.objects.bulk_create(viwers_list)

    def test_redirect_if_user_has_no_corrected_permission_hand_import(self):
        Login = self.client.login(username="test1", password="12345")
        resp = self.client.get(reverse('start-hand-import') + self.test_data_request)
        self.assertEqual(resp.status_code, 403)

    def test_open_sours_if_user_has_permission_hand_import(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse('start-hand-import') + self.test_data_request)
        self.assertEqual(resp.status_code, 200)

    def test_template_hand_import(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse('start-hand-import')+ self.test_data_request)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "webroom/list_viewers.html")

    def test_pagination_is_twelve(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse('start-hand-import') + self.test_data_request)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue(len(resp.context['list_viewers']) == 20)

    def test_lists_all_webroom_and_return_only_my_viwers_hand_import(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse('start-hand-import') + self.test_data_request + '&page=2')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue(len(resp.context['list_viewers']) == 5)

    def test_correct_import(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse('start-hand-import') + self.test_data_request)
        self.assertEqual(resp.status_code, 200)
        viewer = ViewersImport.objects.get(pk=1)
        name_viewer = viewer.name
        email_viewer = viewer.email
        self.assertEqual(resp.context['list_viewers'][0].name, name_viewer)
        self.assertEqual(resp.context['list_viewers'][0].email, email_viewer)


class ImportGetcourseTest(TestCase):
    """Test view CSVFileImportList"""

    def setUp(self) -> None:
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

    def test_redirect_if_user_has_no_corrected_permission_csf_file(self):
        Login = self.client.login(username="test1", password="12345")
        resp = self.client.get(reverse('my-import-getcourse'))
        self.assertEqual(resp.status_code, 403)

    def test_open_sours_if_user_has_permission_csf_file(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse('my-import-getcourse'))
        self.assertEqual(resp.status_code, 200)

    def test_template_csf_file(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse('my-import-getcourse'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "import_gk/list_csv_file.html")


class SessionListTest(TestCase):
    """Test view WebroomSessionBizonListView"""

    def setUp(self) -> None:
        # Создание тестовых пользователей
        user1 = User.objects.create_user(username="test1", password="12345")
        user1.save()
        user2 = User.objects.create_user(username="test2", password="12345")
        user2.save()
        # Выдача тестовому пользователю прав доступа и тестовых токенов
        permission = Permission.objects.get(name='Has request to GK, Bizon')
        user2.user_permissions.add(permission)
        user2.save()

        # Генерация списка сессий
        number_of_session = 50
        session_list = []
        for it in range(number_of_session):
            user_pk = it % 2 + 1
            user = User.objects.get(id=user_pk)
            session_list.append(TrackedSessinBizon(
                user=user,
                session=f"24105:mr{it}",
                description=f"test{it}",
                group_user=f"test{it}-{it}"))
        TrackedSessinBizon.objects.bulk_create(session_list)

    def test_redirect_if_user_has_no_corrected_permission_session_list(self):
        Login = self.client.login(username="test1", password="12345")
        resp = self.client.get(reverse('list-session'))
        self.assertEqual(resp.status_code, 403)

    def test_open_sours_if_user_has_permission_session_list(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse('list-session'))
        self.assertEqual(resp.status_code, 200)

    def test_template_session_list(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse('list-session'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "session/bizon_vebroom_list_tracked.html")

    def test_pagination_is_ten(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse('list-session'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue(len(resp.context['sessions']) == 10)

    def test_lists_all_webroom_and_return_only_my_web(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse('list-session')+'?page=3')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertEqual(len(resp.context['sessions']), 5)


class SessionWebroomListTest(TestCase):
    """Test view SessionWebroomListView"""

    def setUp(self) -> None:
        # Создание тестовых пользователей
        user1 = User.objects.create_user(username="test1", password="12345")
        user1.save()
        user2 = User.objects.create_user(username="test2", password="12345")
        user2.save()
        # Выдача тестовому пользователю прав доступа и тестовых токенов
        permission = Permission.objects.get(name='Has request to GK, Bizon')
        user2.user_permissions.add(permission)
        user2.save()

        session = TrackedSessinBizon.objects.create(
            user=user2,
            session="24105:mr03",
            description="test",
            group_user="test")

        # Генерация списка вебинаров к сессии
        number_of_web = 25
        session_list = []
        for it in range(number_of_web):
            session_list.append(WebroomTransaction(
                event="webinarEnd",
                roomid=f"24105:user1-{it}",
                webinarId=f"24105:user1-web160{it}-02-15T19:00:-{it}",
                session=session,
                user_id=user2))

        WebroomTransaction.objects.bulk_create(session_list)


    def test_redirect_if_user_has_no_corrected_permission_session_list(self):
        Login = self.client.login(username="test1", password="12345")
        resp = self.client.get(reverse('session-bizon', kwargs={"pk": 1, }))
        self.assertEqual(resp.status_code, 403)

    def test_open_sours_if_user_has_permission_session_list(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse('session-bizon', kwargs={"pk": 1, }))
        self.assertEqual(resp.status_code, 200)

    def test_template_session_list(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse('session-bizon', kwargs={"pk": 1, }))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "session/session_bizon.html")

    def test_pagination_is_ten(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse('session-bizon', kwargs={"pk": 1, }))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        # self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue(len(resp.context['session']['webroomtransaction_set']) == 10)

    def test_lists_all_webroom_and_return_only_my_web(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse('session-bizon', kwargs={"pk": 1, })+'?page=3')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        # self.assertTrue(resp.context['is_paginated'] == True)
        self.assertEqual(len(resp.context['session']['webroomtransaction_set']), 5)


class CreateSessionTest(TestCase):
    """Test view WebroomSessionCreateView"""

    def setUp(self) -> None:
        # Создание тестовых пользователей
        user1 = User.objects.create_user(username="test1", password="12345")
        user1.save()
        user2 = User.objects.create_user(username="test2", password="12345")
        user2.save()
        # Выдача тестовому пользователю прав доступа и тестовых токенов
        permission = Permission.objects.get(name='Has request to GK, Bizon')
        user2.user_permissions.add(permission)
        user2.save()


    def test_redirect_if_user_has_no_corrected_permission_session_list(self):
        Login = self.client.login(username="test1", password="12345")
        resp = self.client.get(reverse('session-create'))
        self.assertEqual(resp.status_code, 403)

    def test_open_sours_if_user_has_permission_session_list(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse('session-create'))
        self.assertEqual(resp.status_code, 200)

    def test_template_session_list(self):
        login = self.client.login(username="test2", password="12345")
        resp = self.client.get(reverse('session-create'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "session/session_webinar_create.html")

