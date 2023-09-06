from os.path import basename
from urllib.parse import urlparse
from sentry_sdk import capture_exception
from whatsapp_api_client_python import API as API
from django.http import JsonResponse

from customers.models import Customer

import logging

logger = logging.getLogger(__name__)
ID_INSTANCE = '1101817774'
API_TOKEN_INSTANCE = 'ecad3cbbda704ea0ab0f1a784f527c06938cf64fb3924895a0'

class GreenAPIService:
    def __init__(self):
        self.api = API.GreenApi(ID_INSTANCE, API_TOKEN_INSTANCE)

    def send_message(self, phone_number, message):
        try:
            self.api.sending.sendMessage(f'{phone_number}@c.us', message)
        except Exception as e:
            capture_exception(e)
            logger.error(f"Error sending message to {phone_number}: {e}")

    def send_file(self, phone_number, file_path, message):
        try:
            upload_response = self.api.sending.uploadFile(file_path)
            if upload_response.code == 200:
                url_file = upload_response.data["urlFile"]
                file_name = basename(urlparse(url_file).path)
                self.api.sending.sendFileByUrl(f"{phone_number}@c.us", url_file, file_name, message)
            else:
                error_message = upload_response.data.get("errorMessage", "Unknown error")
                logger.warning(f"Failed to upload file for {phone_number}. Status code: {upload_response.code}. Error message: {error_message}")
        except Exception as e:
            capture_exception(e)
            logger.error(f"Error sending file to {phone_number}: {e}")



def task_send_winner_message(data):
    green_api_service = GreenAPIService()
    file_path = data.get('file_path', 'none')
    phone_number = data.get('phone_number')
    message = data.get('message')
    if file_path != 'none':
        green_api_service.send_file(phone_number, file_path, message)
    elif message:
        green_api_service.send_message(phone_number, message)
