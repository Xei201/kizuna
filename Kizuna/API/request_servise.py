import base64
import json
import requests

from .models import WebroomTransaction, ViewersImport, TokenImport


def get_token_getcourse(request):
    if request.GET.get("token", ''):
        token = request.GET.get("token")
        return str(TokenImport.objects.get(token=token).token_gk)
    else:
        user = request.user
        return str(TokenImport.objects.get(user=user).token_gk)


def get_token_bizon(request):
    if request.GET.get("token", ''):
        token = request.GET.get("token")
        return str(TokenImport.objects.get(token=token).token_bizon)
    else:
        user = request.user
        return str(TokenImport.objects.get(user=user).token_bizon)


def request_biz(webinar_id, request):
    headers = {"X-Token": get_token_bizon(request)}
    url = f"https://online.bizon365.ru/api/v1/webinars/reports/getviewers?webinarId={str(webinar_id)}&skip=0&limit=1000"
    response = requests.get(url, headers=headers)
    return response


def export_bizon(webinar_id, request):
    response_web = request_biz(webinar_id, request)
    dict_users = response_web.json()
    webroom = WebroomTransaction.objects.get(webinarId=webinar_id)
    webroomm_transaction_id = webroom.id
    for user in dict_users["viewers"]:
        viewer = ViewersImport()
        viewer.name = user.get("name", 'Not found')
        viewer.email = user["email"]
        viewer.phone = user.get("phone", 'Not found')
        viewer.view = (int(user["viewTill"]) - int(user['view'])) / 60000
        viewer.buttons = ', '.join([button["id"] for button in user.get("buttons", None)])
        viewer.banners = ', '.join([banner["id"] for banner in user.get("banners", None)])
        viewer.webroom_id = webroomm_transaction_id
        viewer.save()


def import_gk(webinar_id, request):
    webroom = WebroomTransaction.objects.get(webinarId=webinar_id)
    viewers_list = webroom.viewersimport_set.values()
    token_getcourse = get_token_getcourse(request)
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
        r = requests.post(f'https://senseat.getcourse.ru/pl/api/users/', data=data)
    webroom.result_upload = True
    webroom.save()


def get_bizon_web_list(request, webroom_quantity):
    headers = {"X-Token": get_token_bizon(request)}
    date_min = request.GET.get("date_min")
    date_max = request.GET.get("date_max")
    if not date_min:
        url = f"https://online.bizon365.ru/api/v1/webinars/reports/getlist?skip=0&limit={webroom_quantity}"
    else:
        url = f"https://online.bizon365.ru/api/v1/webinars/reports/getlist?skip=0&limit={webroom_quantity}" \
                f"&minDate={date_min}T00:00:00&maxDate={date_max}T00:00:00"
    response = requests.get(url, headers=headers)
    dict_webroom = response.json()
    return dict_webroom["list"]