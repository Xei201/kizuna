import csv
import logging
from io import StringIO

from django.core.exceptions import ObjectDoesNotExist
from API.core.exceptions import NoModelFoundException
from API.core.request_service import RequestGetcorse
from API.models import FileImportGetcourse, WebroomTransaction, ViewersImport
from django.utils.translation import gettext_lazy as _


logger = logging.getLogger(__name__)


class ImportGetcorseValidation():
    """Занимается валидацией данных для импорта в Getcourse и вызовами импортов из request_service"""

    def __init__(self, request, **kwargs):
        self.request = request
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_choices_field(self) -> list:
        csv_data = self._get_csv_data()
        row1 = next(csv_data)
        row2 = next(csv_data)
        row0 = [i for i in range(len(row1))]
        row_sum = [f"{row1[i]} -- {row2[i]}" for i in range(len(row1))]
        list_choices_tuple = list(zip(row0, row_sum))
        return list_choices_tuple

    def start_import_to_getcourse_api(self, webroom):
        imp = RequestGetcorse(self.request)
        if imp.import_viewers(webroom):
            logger.info(f"Success API import to Getcourse viewers from API to Bizon "
                        f"request {self.request}")
        else:
            logger.warning(f"Fallen API import to Getcourse viewers from API to Bizon "
                           f"request {self.request}")

    def start_import_to_getcorse_csv(self, webroom):
        imp = RequestGetcorse(self.request)
        if imp.import_viewers(webroom):
            logger.info(f"Success import to Getcourse viewers from CSV to Bizon "
                        f"request {self.request}")
        else:
            logger.warning(f"Fallen import to Getcourse viewers from CSV to Bizon "
                           f"request {self.request}")

    def start_upload_viewers_csv_to_bd(self, form_data: dict) -> bool:
        csv_data = self._get_csv_data()
        file = self._get_file()
        webroom = WebroomTransaction.objects.create(
            event="Import CSV",
            roomid=str(file),
            webinarId=file.group_user,
            user_id=self.request.user
        )
        next(csv_data)
        control_amount_viewer = 0
        for row in csv_data:
            control_amount_viewer += 1
            if not (ViewersImport.objects.filter(webroom_id=webroom.id) &
                    ViewersImport.objects.filter(email=row[int(form_data["email"])])).exists():
                viewer = ViewersImport()
                viewer.name = row[int(form_data["name"])]
                viewer.email = row[int(form_data["email"])]
                viewer.phone = row[int(form_data["phone"])]
                viewer.view = 0
                viewer.buttons = ""
                viewer.banners = ""
                viewer.webroom_id = webroom.id
                viewer.save()
        if control_amount_viewer > 0:
            logger.info(f"Success export viewers {webroom} from CSV to BD"
                        f"request {self.request}")
            return True
        else:
            logger.warning(f"Fallen export viewers {webroom} from CSV to BD "
                           f"request {self.request}")
            return False

    def _get_file(self):
        user = self.request.user
        try:
            return FileImportGetcourse.objects.filter(user=user).last()
        except ObjectDoesNotExist:
            logger.info(f"{user} no found file")
            exception_msg = "No found file"
            raise NoModelFoundException(_(exception_msg))

    def _get_csv_data(self):
        file_upload = self._get_file().file
        file = file_upload.read().decode('utf-8')
        return csv.reader(StringIO(file), delimiter=',')


class ImportGetcourseValidationPK(ImportGetcorseValidation):
    def _get_file(self):
        try:
            return FileImportGetcourse.objects.get(pk=self.pk)
        except ObjectDoesNotExist:
            logger.info(f"Objects{self.pk} no found file")
            exception_msg = "No found file"
            raise NoModelFoundException(_(exception_msg))

