import base64
import json
import requests

from .models import WebroomTransaction, ViewersImport, TokenImport


def get_token_getcourse(request):
    token = request.GET.get("token")
    return str(TokenImport.objects.get(token=token).token_gk)


def get_token_bizon(request):
    token = request.GET.get("token")
    return str(TokenImport.objects.get(token=token).token_bizon)


def request_biz(webinar_id, request):
    headers = {"X-Token": get_token_bizon(request)}
    url = f"https://online.bizon365.ru/api/v1/webinars/reports/getviewers?webinarId={str(webinar_id)}&skip=0&limit=100"
    response = requests.get(url, headers=headers)
    return response


def export_bizon(webinar_id, request):
    response_web = request_biz(webinar_id, request)
    dict_users = response_web.json()
    webroom = WebroomTransaction.objects.get(webinarId=webinar_id)
    webroomm_transaction_id = webroom.id
    for user in dict_users["viewers"]:
        viewer = ViewersImport()
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
        r = requests.post(f'https://dimapravvideo.getcourse.ru/pl/api/users/', data=data)
        if r.status_code == 200:
            viewer.import_to_gk = True
            viewer.save()
    webroom.result_upload = True
    webroom.save()

