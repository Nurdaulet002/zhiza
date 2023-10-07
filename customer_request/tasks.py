import logging
import requests
import json
from sentry_sdk import capture_exception
from whatsapp_api_client_python import API as API

from django.http import JsonResponse
from django.utils import timezone

from customer_request.models import CustomerRequest

logger = logging.getLogger(__name__)


def my_scheduled_job(phone_number, token):
    BASE_URL = 'https://gate.whapi.cloud/'
    message = 'Оцените по  5 балльной шкале:\n\n1 – Неудовлетворительно\n2 – Ниже среднего\n3 – Средне\n4 – Хорошо\n5 – Отлично\n\nОтправьте только одну цифру!!!'
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

    result = requests.post(f'{BASE_URL}messages/text', data=json.dumps(data), headers=headers)
    print("Job is running...")
    return JsonResponse({'data': result.data})


def task_send_message_order_completed(data):

    try:
        BASE_URL = 'https://gate.whapi.cloud/'
        token = data.get('token')
        card_number = data.get('card_number')
        branch = data.get('branch')
        message = 'Ваш заказ готов, можете забрать!'

        customer_requests = CustomerRequest.objects.filter(
            card_number=card_number, branch=branch, status=1)
        for customer_request in customer_requests:

            data = {
                'to': f'{customer_request.customer.phone_number}@s.whatsapp.net',
                'body': message,
                'typing_time': 0,
                'view_once': True,
            }

            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }

            requests.post(f'{BASE_URL}messages/text', data=json.dumps(data), headers=headers)
            customer_request.status = 2
            customer_request.datetime = timezone.now()
            customer_request.save()

    except Exception as e:
        capture_exception(e)
        logger.error(f"Error: {e}")

