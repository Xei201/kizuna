import base64
import json
import logging
import requests
from os import path

from Kizuna import settings
from API.models import WebroomTransaction, ViewersImport, TokenImport

logger = logging.getLogger(__name__)


class RequestImport():
    """Интерфейс хранящий методы получения token сервисов"""

    def __init__(self, request):
        self.request = request

    def _get_token_getcourse(self) -> str:
        """Возвращает token GK"""

        params_user = self._get_user()
        return TokenImport.objects.get(**params_user).token_gk

    def _get_token_bizon(self) -> str:
        """Возвращает token Bizon"""

        params_user = self._get_user()
        return TokenImport.objects.get(**params_user).token_bizon

    def _get_url_getcourse_api(self) -> str:
        """Возвращает url API GK"""

        params_user = self._get_user()
        name_gk = TokenImport.objects.get(**params_user).name_gk
        getcourse_api = "https://" + name_gk + settings.URL_GETCOURSE_API
        return getcourse_api

    def _get_user(self) -> dict:
        """Поиск юзера в системе либо через request либо через token"""

        params_user = {}
        if self.request.GET.get("token"):
            params_user["token"] = self.request.GET.get("token")
        else:
            params_user["user"] = self.request.user
        return params_user


class RequestBizon(RequestImport):
    """Сервис обращающийся к Bizon для получения списков вебинаров и зрителей"""

    def export_viwers(self, webinar_id: str) -> bool:
        """Загрузка списка зрителей в БД"""

        list_viewers = self.get_viewers(webinar_id)

        if list_viewers is None or len(list_viewers) == 0:
            logger.warning(f"Error export viewers Bizon for web {webinar_id},"
                           f"from request {self.request}")
            return False

        if list_viewers[0] == "It is test data":
            return True

        webroom = WebroomTransaction.objects.get(webinarId=webinar_id)
        webroomm_transaction_id = webroom.id
        for user in list_viewers:
            if not (ViewersImport.objects.filter(webroom_id=webroomm_transaction_id) &
                    ViewersImport.objects.filter(email=user["email"])).exists():
                viewer = ViewersImport()
                viewer.name = user.get("name", 'Not found')
                viewer.email = user["email"]
                viewer.phone = user.get("phone", 'Not found')
                viewer.view = (int(user["viewTill"]) - int(user['view'])) / 60000
                viewer.buttons = ', '.join([button["id"] for button in user.get("buttons", None)])
                viewer.banners = ', '.join([banner["id"] for banner in user.get("banners", None)])
                viewer.webroom_id = webroomm_transaction_id
                viewer.save()
        logger.info(f"Success export viewers {webinar_id} from Bizon to BD")
        return True

    def get_web_list(self, webroom_quantity: int) -> list:
        """Получение списка вебинаров"""

        headers = self._get_headers()
        date_min, date_max = self._get_date()

        if date_min > date_max:
            logger.warning(f"Uncorrect date of request {self.request}")
            list_webroom = ["Error", "Uncorrect date, end date must be "
                                     "greater than start date "]
            return list_webroom

        if headers["X-Token"] == settings.BIZON_TEST_API:
            list_webroom = self._get_test_data_webroom()
            return list_webroom

        params = {
            "skip": 0,
            "limit": webroom_quantity,
            "minDate": date_min,
            "maxDate": date_max}

        url = path.join(settings.URL_BIZON_API, settings.URL_BIZON_WEBINAR, 'getlist')
        try:
            response = requests.get(url, headers=headers, params=params)
        except ConnectionError:
            logger.warning(f"Connection Error from request {self.request}")
            list_webroom = ["Error", "Connection Error to List Web, try later"]
            return list_webroom

        if response.status_code == 200:
            list_webroom = response.json()
            logger.info(f"Success web list from Bizon to view "
                        f"from request {self.request}")
            return list_webroom["list"]
        else:
            logger.info(f"Response web list from request {self.request}"
                           f"web list return code {response.status_code}")
            list_webroom = ["Error", "Connection Error to List Web, try later"]
            return list_webroom

    def get_viewers(self, webinar_id: str) -> list:
        """Получение списка зрителей конкретного вебинара"""

        headers = self._get_headers()

        # Обработка тестового запроса
        if headers["X-Token"] == settings.BIZON_TEST_API:
            list_users = []
            list_users.append("It is test data")
            return list_users

        params = {
            "webinarId": webinar_id,
            "skip": 0,
            "limit": 1000}
        url = path.join(settings.URL_BIZON_API, settings.URL_BIZON_WEBINAR, 'getviewers')
        try:
            response = requests.get(url, headers=headers, params=params)
        except ConnectionError:
            logger.info(f"Response viewers from request {self.request}"
                           f"web list return code {response.status_code}")
            return None

        if response.status_code == 200:
            list_users = response.json()
            logger.info(f"Success viewers list from Bizon to view"
                        f"from request {self.request}")
            return list_users["viewers"]
        else:
            logger.warning(f"Response from request {self.request}"
                           f"viewers list return code {response.status_code}")
            return None

    def _get_headers(self) -> dict:
        """Генерация хедера"""

        token = self._get_token_bizon()
        return {"X-Token": token}

    def _get_date(self) -> tuple:
        """Загрузка дат интервала запроса по выборке"""

        date_min = self.request.GET.get("date_min", "")
        date_max = self.request.GET.get("date_max", "")

        return date_min, date_max

    def _get_test_data_webroom(self) -> dict:
        """Получает список тестовых вебинаров из БД
        в обход базовой работы класса с внешним ресурсом"""

        user = TokenImport.objects.get(token_bizon=settings.BIZON_TEST_API).user
        dict_webroom = WebroomTransaction.objects.filter(user_id=user)
        return dict_webroom

    @classmethod
    def test_token_bizon(cls, token: str) -> bool:
        """Проверка токена на актуальность"""

        if token == settings.BIZON_TEST_API:
            return True

        headers = {"X-Token": token}
        params = {"limit": 1}
        url = path.join(settings.URL_BIZON_API, settings.URL_BIZON_WEBINAR, 'getlist')
        try:
            response = requests.get(url, headers=headers, params=params)
            logger.info("Success test token Bizon")
            return response.status_code == 200
        except ConnectionError:
            logger.info(f"Unsuccess test token Bizon")
            return False


class RequestGetcorse(RequestImport):
    """Сервис импортирующий людей на Getcourse"""

    def import_viewers(self, webinar_id: str) -> bool:
        """Импорт списка пользователей на Getcourse"""

        webroom = WebroomTransaction.objects.get(webinarId=webinar_id)
        viewers_list = webroom.viewersimport_set.values()
        success = 0
        for viewer in viewers_list:
            if self.import_viever(viewer, webinar_id):
                success += 1

        if len(viewers_list) > 0:
            if round(success / len(viewers_list), 2) > settings.IMPORT_SUCCESS_RATE:
                webroom.result_upload = True
                webroom.save(update_fields=('result_upload',))
                logger.info(f"Success import to Getcourse from webinar {webinar_id}")
                return True
            else:
                logger.info(f"Unsuccess import to Getcourse from webinar {webinar_id},"
                            f"success rate minimal")
                return False
        else:
            logger.info(f"Unsuccess import to Getcourse from webinar {webinar_id} viewers = 0")
            return True

    def import_viever(self, viewer: dict, webinar_id: str) -> bool:
        """Производит импорт одного зрителя на Getcourse"""
        token_getcourse = self._get_token_getcourse()

        # Start for test VIEW
        if token_getcourse == settings.GETCOURSE_TEST_API:
            return True

        user = {
            "user": {
                "email": viewer["email"],
                "phone": viewer["phone"],
                "addfields": {"Время на вебинаре (минуты)": viewer["view"],
                              "Клики на кнопки": viewer["buttons"],
                              "Клики на баннеры": viewer["banners"],
                              },
                "group_name": [webinar_id]},
            "system": {
                "refresh_if_exists": 1}}
        params = json.dumps(user).encode('utf-8')
        encoded_params = base64.b64encode(params)
        data = {
            'action': 'add',
            'key': token_getcourse,
            'params': encoded_params
        }
        url = path.join(self._get_url_getcourse_api(), settings.URL_GETCOURSE_API_USERS)
        try:
            r = requests.post(url, data=data)
            if r.json()["result"]["success"]:
                ViewersImport.objects.filter(id=viewer["id"]).update(import_to_gk=True)
                return True
            else:
                logger.info(f"Unsuccess import to Getcourse user {viewer['email']}"
                            f"from webinar {webinar_id}, error massage:"
                            f"{r.json()['result']['error_message']}")
                return False
        except ConnectionError:
            logger.warning(f"Unsuccess import to Getcourse user {viewer['email']} "
                           f"from webinar {webinar_id}")
            return False

    @classmethod
    def test_token_gk(cls, token: str, name_gk: str) -> bool:
        """Проверка токена на актуальность"""

        if token == settings.GETCOURSE_TEST_API:
            return True

        data = {
            'action': 'add',
            'key': token,
            'params': 'test'
        }
        url = path.join(("https://" + name_gk + settings.URL_GETCOURSE_API), settings.URL_GETCOURSE_API_USERS)
        logger.info("Success test token Getcourse")
        try:
            r = requests.post(url, data=data)
            logger.info(f"Success test token Getcourse {name_gk}")
            return r.json()["success"]
        except ConnectionError:
            logger.info(f"Unsuccess test token Getcourse {name_gk}")
            return False
        except json.JSONDecodeError:
            logger.info(f"Unsuccess test token Getcourse {name_gk}")
            return False




