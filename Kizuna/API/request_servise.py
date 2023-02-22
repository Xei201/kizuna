import base64
import json
import requests
from os import path

from Kizuna import settings
from general.exceptions import NoValidTokenService, NoSpecifiedTokenService
from .models import WebroomTransaction, ViewersImport, TokenImport


class RequestImport():
    def __init__(self, request):
        self.request = request

    def _get_token_getcourse(self) -> str:
        params_user = {}
        if self.request.GET.get("token", ''):
            params_user["token"] = self.request.GET.get("token")
        else:
            params_user["user"] = self.request.user

        return TokenImport.objects.get(**params_user).token_gk

    def _get_token_bizon(self) -> str:
        params_user = {}
        if self.request.GET.get("token", ''):
            params_user["token"] = self.request.GET.get("token")
        else:
            params_user["user"] = self.request.user

        return TokenImport.objects.get(**params_user).token_bizon

    def _get_url_getcourse_api(self):
        params_user = {}
        if self.request.GET.get("token", ""):
            params_user["token"] = self.request.GET.get("token", "")
        else:
            params_user["user"] = self.request.user
        name_gk = TokenImport.objects.get(**params_user).name_gk
        getcourse_api = "https://" + name_gk + settings.URL_GETCOURSE_API
        return getcourse_api

    # Продумать систему валидации и работу исключения
    @classmethod
    def is_valid_token(cls, token):
        if token is None:
            raise NoSpecifiedTokenService()
        if len(token) < 10:
            raise NoValidTokenService()


class RequestBizon(RequestImport):
    def export_viwers(self, webinar_id: str) -> None:
        dict_viewers = self.get_viewers(webinar_id)
        webroom = WebroomTransaction.objects.get(webinarId=webinar_id)
        webroomm_transaction_id = webroom.id
        for user in dict_viewers:
            viewer = ViewersImport()
            viewer.name = user.get("name", 'Not found')
            viewer.email = user["email"]
            viewer.phone = user.get("phone", 'Not found')
            viewer.view = (int(user["viewTill"]) - int(user['view'])) / 60000
            viewer.buttons = ', '.join([button["id"] for button in user.get("buttons", None)])
            viewer.banners = ', '.join([banner["id"] for banner in user.get("banners", None)])
            viewer.webroom_id = webroomm_transaction_id
            viewer.save()

    def get_web_list(self, webroom_quantity: int) -> dict:
        token = self._get_token_bizon()
        self.is_valid_token(token)
        headers = {"X-Token": token}
        date_min = self.request.GET.get("date_min")
        date_max = self.request.GET.get("date_max")
        params = {
            "skip": 0,
            "limit": webroom_quantity,
            "minDate": date_min,
            "maxDate": date_max}
        url = path.join(settings.URL_BIZON_API, settings.URL_BIZON_WEBINAR, 'getlist')
        response = requests.get(url, headers=headers, params=params)
        dict_webroom = response.json()
        return dict_webroom["list"]

    def get_viewers(self, webinar_id: str) -> dict:
        token = self._get_token_bizon()
        self.is_valid_token(token)
        headers = {"X-Token": token}
        params = {
            "webinarId": webinar_id,
            "skip": 0,
            "limit": 1000}
        url = path.join(settings.URL_BIZON_API, settings.URL_BIZON_WEBINAR, 'getviewers')
        response = requests.get(url, headers=headers, params=params)
        dict_users = response.json()
        return dict_users["viewers"]


class RequestGetcorse(RequestImport):
    def import_viewers(self, webinar_id: str) -> None:
        webroom = WebroomTransaction.objects.get(webinarId=webinar_id)
        viewers_list = webroom.viewersimport_set.values()
        token_getcourse = self._get_token_getcourse()
        self.is_valid_token(token_getcourse)
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
            r = requests.post(url, data=data)
            if r.json()["success"]:
                ViewersImport.objects.filter(id=viewer["id"]).update(import_to_gk=True)
        webroom.result_upload = True
        webroom.save()
