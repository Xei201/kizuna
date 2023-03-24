import functools
import logging

from django.db import transaction
from django.http import JsonResponse
from rest_framework.exceptions import PermissionDenied

JSON_DAMP_PATAMS = {
    "ensure_ascii": False
}

logger = logging.getLogger(__name__)


def ret(json_objects, status=200):
    """ОТдаёт JSON с правильным HTTP заголовками и в читаймом виде
    в браузере в случае кирилицы"""

    return JsonResponse(
        json_objects,
        status=status,
        safe=not isinstance(json_objects, list),
        json_dumps_params=JSON_DAMP_PATAMS
    )


def error_response(exception):
    """Формирует HTTP ответ с описание ошибки"""

    res = {"errorMessage": str(exception),
           "tracerback": exception.format_exc()}
    return ret(res, status=400)


def base_exception(fn):
    """Декоратор для всех представлений обрабатывающий исключения"""

    @functools.wraps(fn)
    def inner(request, *arg, **kwargs):
        try:
            with transaction.atomic():
                return fn(request, *arg, **kwargs)
        except Exception as e:
            logger.error(f"Generic global Except, Exception message: {str(e)}")
            return error_response(e)
    return inner


class BaseExceptions():
    """Базовый класс для всех предтавлений обрабатывающих исключения"""

    def dispatch(self, request, *arg, **kwargs):
        try:
            response = super().dispatch(request, *arg, **kwargs)
        except Exception as e:
            logger.error(f"Generic global Except, Exception message: {str(e)}")
            return self._response({"error_message": str(e)}, status=400)

        if isinstance(response, (dict, list)):
            return self._response(response)
        else:
            return response

    @staticmethod
    def _response(data, *, status=200):
        return JsonResponse(
            data,
            status=status,
            safe=not isinstance(data, list),
            json_dumps_params=JSON_DAMP_PATAMS
        )
    pass







