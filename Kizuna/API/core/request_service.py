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
        if self.request.GET.get("token", ""):
            params_user["token"] = self.request.GET.get("token", "")
        else:
            params_user["user"] = self.request.user
        return params_user


class RequestBizon(RequestImport):
    """Сервис обращающийся к Bizon для получения списков вебинаров и зрителей"""

    def export_viwers(self, webinar_id: str) -> bool:
        """Загрузка списка зрителей в БД"""

        dict_viewers = self.get_viewers(webinar_id)
        if dict_viewers is None:
            logger.warning(f"Error export viewers Bizon for web {webinar_id},"
                           f"from request {self.request}")
            return False

        webroom = WebroomTransaction.objects.get(webinarId=webinar_id)
        webroomm_transaction_id = webroom.id
        for user in dict_viewers:
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

    def get_web_list(self, webroom_quantity: int) -> dict:
        """Получение списка вебинаров"""

        headers = self._get_headers()
        date_min = self.request.GET.get("date_min")
        date_max = self.request.GET.get("date_max")
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
            dict_webroom = ["Error", "Connection Error to List Web, try later"]
            return dict_webroom

        if response.status_code == 200:
            dict_webroom = response.json()
            logger.info(f"Success web list from Bizon to view "
                        f"from request {self.request}")
            return dict_webroom["list"]
        else:
            logger.info(f"Response web list from request {self.request}"
                           f"web list return code {response.status_code}")
            dict_webroom = ["Error", "Connection Error to List Web, try later"]
            return dict_webroom

    def get_viewers(self, webinar_id: str) -> dict:
        """Получение списка зрителей конкретного вебинара"""

        headers = self._get_headers()
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
            dict_users = response.json()
            logger.info(f"Success viewers list from Bizon to view"
                        f"from request {self.request}")
            return dict_users["viewers"]
        else:
            logger.warning(f"Response from request {self.request}"
                           f"viewers list return code {response.status_code}")
            return None

    def _get_headers(self) -> dict:
        """Генерация хедера"""

        token = self._get_token_bizon()
        return {"X-Token": token}

    @classmethod
    def test_token_bizon(cls, token: str) -> bool:
        """Проверка токена на актуальность"""

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
        token_getcourse = self._get_token_getcourse()
        success = 0
        for viewer in viewers_list:
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
                    success += 1
                else:
                    logger.info(f"Unsuccess import to Getcourse user {viewer['email']}"
                                f"from webinar {webinar_id}, error massage:"
                                f"{r.json()['result']['error_message']}")
            except ConnectionError:
                logger.warning(f"Unsuccess import to Getcourse user {viewer['email']} "
                            f"from webinar {webinar_id}")

        if len(viewers_list) > 0:
            if round(success / len(viewers_list), 2) > settings.IMPORT_SUCCESS_RATE:
                webroom.result_upload = True
                webroom.save()
                logger.info(f"Success import to Getcourse from webinar {webinar_id}")
                return True
            else:
                logger.info(f"Unsuccess import to Getcourse from webinar {webinar_id},"
                            f"success rate < {settings.IMPORT_SUCCES_RATE}")
                return False
        else:
            logger.info(f"Unsuccess import to Getcourse from webinar {webinar_id} viewers = 0")
            return True

    @classmethod
    def test_token_gk(cls, token, name_gk):
        """Проверка токена на актуальность"""

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
