import requests
import base64
import json
from sentry_sdk import capture_exception


import logging

logger = logging.getLogger(__name__)


def task_send_winner_message(data):
    try:
        phone_number = data.get('phone_number')
        token = data.get('token')
        message = data.get('message')
        file_path = data.get('file_path', 'none')
        file_name = file_path[42:]

        if file_path != 'none':

            with open(file_path, "rb") as image_file:
                base64_encoded = base64.b64encode(image_file.read()).decode('utf-8')

            url = "https://gate.whapi.cloud/messages/image"

            payload = {
                "media": f"data:image/png;name={file_name};base64,{base64_encoded}",
                "to": f"{phone_number}@s.whatsapp.net",
                "caption": f"{message}"
            }
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "authorization": f"Bearer {token}"
            }

            requests.post(url, json=payload, headers=headers)
        elif message:
            BASE_URL = 'https://gate.whapi.cloud/'
            data = {
                'to': f'{phone_number}@s.whatsapp.net',
                'body': message,
                'typing_time': 0,
                'view_once': True,
            }

            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }

            requests.post(f'{BASE_URL}messages/text', data=json.dumps(data), headers=headers)

    except Exception as e:
        capture_exception(e)
        logger.error(f"Error in task_send_winner_message: {e}")

