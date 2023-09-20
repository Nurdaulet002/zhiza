from os.path import basename
from urllib.parse import urlparse
from sentry_sdk import capture_exception
from whatsapp_api_client_python import API as API
from django.http import JsonResponse

from customers.models import Customer

import logging

logger = logging.getLogger(__name__)
ID_INSTANCE = '1101817797'
API_TOKEN_INSTANCE = '444b8de1fd9d4c38a1cf4df0a43770b924f64bf46db349ac95'


class GreenAPIService:
    def __init__(self, instance_id, token):
        self.api = API.GreenApi(instance_id, token)

    def send_message(self, phone_number, message):
        try:
            self.api.sending.sendMessage(f'{phone_number}@c.us', message)
        except Exception as e:
            capture_exception(e)
            logger.error(f"Error sending message to {phone_number}: {e}")

    def send_file(self, phone_number, file_path, message):
        file_name = file_path[42:]
        print(file_name)
        try:
            self.api.sending.sendFileByUpload(f"{phone_number}@c.us", file_path, file_name, message)
        except Exception as e:
            capture_exception(e)
            logger.error(f"Error sending file to {phone_number}: {e}")

def task_send_winner_message(data):
    try:
        phone_number = data.get('phone_number')
        instance_id = data.get('instance_id')
        token = data.get('token')
        message = data.get('message')
        file_path = data.get('file_path', 'none')

        green_api_service = GreenAPIService(instance_id, token)

        if file_path != 'none':
            green_api_service.send_file(phone_number, file_path, message)
        elif message:
            green_api_service.send_message(phone_number, message)
    except Exception as e:
        capture_exception(e)
        logger.error(f"Error in task_send_winner_message: {e}")

