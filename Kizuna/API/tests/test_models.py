from django.contrib.auth.models import User
from django.test import TestCase

from API.models import WebroomTransaction, TokenImport, ViewersImport, TrackedSessinBizon


class WebroomTransactionModelTest(TestCase):
    """Test for WebroomTransaction"""

    @classmethod
    def setUpTestData(cls):
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user1.save()
        WebroomTransaction.objects.create(
            event="webinarEnd",
            roomid="24105:web160222",
            webinarId="24105:web160222*2023-02-15T19:00:00",
            user_id=test_user1
        )

    def test_event_field(self):
        web = WebroomTransaction.objects.get(id=1)
        field = web._meta.get_field("event")
        field_event = field.verbose_name
        max_length = field.max_length
        self.assertEquals(field_event, "Type_event")
        self.assertEquals(max_length, 200)

    def test_roomid_field(self):
        web = WebroomTransaction.objects.get(id=1)
        field = web._meta.get_field("roomid")
        field_verbose = field.verbose_name
        max_length = field.max_length
        self.assertEquals(field_verbose, "ID_number_webinar_room")
        self.assertEquals(max_length, 200)

    def test_webinarId_field(self):
        web = WebroomTransaction.objects.get(id=1)
        field = web._meta.get_field("webinarId")
        field_verbose = field.verbose_name
        max_length = field.max_length
        self.assertEquals(field_verbose, "ID_webinar_event")
        self.assertEquals(max_length, 200)

    def test_date_field(self):
        web = WebroomTransaction.objects.get(id=1)
        create = web._meta.get_field("create").auto_now_add
        update = web._meta.get_field("update").auto_now
        self.assertEquals(create, True)
        self.assertEquals(update, True)

    def test_upload_field(self):
        web = WebroomTransaction.objects.get(id=1)
        start_up = web.start_upload
        result_up = web.result_upload
        self.assertEquals(start_up, False)
        self.assertEquals(result_up, False)

    def test_get_absolut_url(self):
        web = WebroomTransaction.objects.get(id=1)
        url = web.get_absolute_url()
        self.assertEquals(url, "/my_webroom/detail/1")

    def test_get_import_url(self):
        web = WebroomTransaction.objects.get(id=1)
        url = web.get_import_url()
        self.assertEquals(url, "/my_webroom/detail/1/reimport")

    def test_get_export_url(self):
        web = WebroomTransaction.objects.get(id=1)
        url = web.get_export_csv_url()
        self.assertEquals(url, "/my_webroom/detail/1/upload")

    def test_str(self):
        web = WebroomTransaction.objects.get(id=1)
        name = web.webinarId
        self.assertEquals(str(web), name)


class TokenImportModelTest(TestCase):
    """Test for TokenImport"""

    @classmethod
    def setUpTestData(cls):
        user_test = User.objects.create_user(username="user", password="12345")
        user_test.save()
        TokenImport.objects.create(user=user_test)

    def test_token_gk(self):
        user = User.objects.get(id=1)
        token = TokenImport.objects.get(user=user)
        token_field = token._meta.get_field("token_gk")
        token_verbose = token_field.verbose_name
        max_length = token_field.max_length
        default_val = token.token_gk
        self.assertEquals(token_verbose, "token gk")
        self.assertEquals(max_length, 260)
        self.assertEquals(default_val, None)

    def test_name_gk(self):
        user = User.objects.get(id=1)
        token = TokenImport.objects.get(user=user)
        token_field = token._meta.get_field("name_gk")
        token_verbose = token_field.verbose_name
        max_length = token_field.max_length
        default_val = token.name_gk
        self.assertEquals(token_verbose, "name gk")
        self.assertEquals(max_length, 200)
        self.assertEquals(default_val, None)

    def test_token_bizon(self):
        user = User.objects.get(id=1)
        token = TokenImport.objects.get(user=user)
        token_field = token._meta.get_field("token_bizon")

        token_verbose = token_field.verbose_name
        max_length = token_field.max_length
        default_val = token.token_bizon
        self.assertEquals(token_verbose, "token bizon")
        self.assertEquals(max_length, 2600)
        self.assertEquals(default_val, None)

    def test_date_field(self):
        user = User.objects.get(id=1)
        token = TokenImport.objects.get(user=user)
        create = token._meta.get_field("create").auto_now_add
        update = token._meta.get_field("update").auto_now
        self.assertEquals(create, True)
        self.assertEquals(update, True)

    def test_str(self):
        user = User.objects.get(id=1)
        token = TokenImport.objects.get(user=user)
        token_str = token.user.username
        self.assertEquals(str(token), token_str)


class ViewersImportModelTest(TestCase):
    """Test for ViewersImport"""

    @classmethod
    def setUpTestData(cls):
        user_test = User.objects.create_user(username="user", password="1234")
        user_test.save()
        webroom = WebroomTransaction.objects.create(
            event="webinarEnd",
            roomid="24105:web160222",
            webinarId="24105:web160222*2023-02-15T19:00:00",
            user_id=user_test
        )
        ViewersImport.objects.create(
            email="test@test.rg",
            phone="23423423",
            view="100",
            webroom=webroom,
        )

    def test_name_field(self):
        viewer = ViewersImport.objects.get(id=1)
        viewers_field = viewer._meta.get_field("name")
        viewer_verbose = viewers_field.verbose_name
        max_length = viewers_field.max_length
        default_val = viewer.name
        self.assertEquals(viewer_verbose, "name")
        self.assertEquals(max_length, 200)
        self.assertEquals(default_val, 'Not found')

    def test_email_field(self):
        viewer = ViewersImport.objects.get(id=1)
        viewers_field = viewer._meta.get_field("email")
        viewer_verbose = viewers_field.verbose_name
        max_length = viewers_field.max_length
        self.assertEquals(viewer_verbose, "email")
        self.assertEquals(max_length, 200)

    def test_phone_field(self):
        viewer = ViewersImport.objects.get(id=1)
        viewers_field = viewer._meta.get_field("phone")
        viewer_verbose = viewers_field.verbose_name
        max_length = viewers_field.max_length
        self.assertEquals(viewer_verbose, "phone")
        self.assertEquals(max_length, 200)

    def test_view_field(self):
        viewer = ViewersImport.objects.get(id=1)
        viewers_field = viewer._meta.get_field("view")
        viewer_verbose = viewers_field.verbose_name
        max_length = viewers_field.max_length
        self.assertEquals(viewer_verbose, "view")
        self.assertEquals(max_length, 200)

    def test_button_field(self):
        viewer = ViewersImport.objects.get(id=1)
        viewers_field = viewer._meta.get_field("buttons")
        viewer_verbose = viewers_field.verbose_name
        max_length = viewers_field.max_length
        default_val = viewer.buttons
        self.assertEquals(viewer_verbose, "buttons")
        self.assertEquals(max_length, 200)
        self.assertEquals(default_val, None)

    def test_banner_field(self):
        viewer = ViewersImport.objects.get(id=1)
        viewers_field = viewer._meta.get_field("banners")
        viewer_verbose = viewers_field.verbose_name
        max_length = viewers_field.max_length
        default_val = viewer.buttons
        self.assertEquals(viewer_verbose, "banners")
        self.assertEquals(max_length, 200)
        self.assertEquals(default_val, None)

    def test_date_field(self):
        viewer = ViewersImport.objects.get(id=1)
        create = viewer._meta.get_field("create").auto_now_add
        self.assertEquals(create, True)

    def test_import_field(self):
        viewer = ViewersImport.objects.get(id=1)
        imp = viewer.import_to_gk
        self.assertEquals(imp, False)

    def test_str(self):
        viewer = ViewersImport.objects.get(id=1)
        viewer_str = viewer.email
        self.assertEquals(str(viewer), viewer_str)


class TrackedSessinBizonTest(TestCase):
    """Test for TrackedSessinBizon"""

    @classmethod
    def setUpTestData(cls):
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user1.save()
        TrackedSessinBizon.objects.create(
            session="24105:web230622",
            description="test",
            group_user="test3",
            user=test_user1
        )

    def test_session_field(self):
        session = TrackedSessinBizon.objects.get(id=1)
        session_field = session._meta.get_field("session")
        max_length = session_field.max_length
        self.assertEquals(max_length, 200)

    def test_description_field(self):
        session = TrackedSessinBizon.objects.get(id=1)
        session_field = session._meta.get_field("description")
        max_length = session_field.max_length
        self.assertEquals(max_length, 200)

    def test_group_user_field(self):
        session = TrackedSessinBizon.objects.get(id=1)
        session_field = session._meta.get_field("group_user")
        max_length = session_field.max_length
        self.assertEquals(max_length, 200)

    def test_str(self):
        session = TrackedSessinBizon.objects.get(id=1)
        session_session = session.session
        self.assertEquals(str(session), session_session)

    def test_get_absolute_url(self):
        web = TrackedSessinBizon.objects.get(id=1)
        url = web.get_absolute_url()
        self.assertEquals(url, "setting/my/bison/session/1")

    def test_get_update_url(self):
        web = TrackedSessinBizon.objects.get(id=1)
        url = web.get_absolute_url()
        self.assertEquals(url, "setting/my/bison/session/update/1")