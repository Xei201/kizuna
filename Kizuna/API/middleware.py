import logging
import time

logger = logging.getLogger("time_request_control")


class RequestTimeControl:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        time_point = time.monotonic()

        response = self.get_response(request)

        logger.info(
            f'Время запроса запроса {request.path} - '
            f'{time.monotonic() - time_point:.3f} сек.'
        )

        return response
