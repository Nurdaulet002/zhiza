import logging
from sentry_sdk import capture_exception
from whatsapp_api_client_python import API as API

from django.http import JsonResponse
from django.utils import timezone

from customer_request.models import CustomerRequest

logger = logging.getLogger(__name__)


def my_scheduled_job(phone_number, instance_id, token):
    greenAPI = API.GreenApi(instance_id, token)
    message = 'Оцените по  5 балльной шкале:\n\n1 – Неудовлетворительно\n2 – Ниже среднего\n3 – Средне\n4 – Хорошо\n5 – Отлично\n\nОтправьте только одну цифру!!!'
    result = greenAPI.sending.sendMessage(f'{phone_number}@c.us', message)
    print("Job is running...")
    return JsonResponse({'data': result.data})


def task_send_message_order_completed(data):
    try:
        instance_id = data.get('instance_id')
        token = data.get('token')
        card_number = data.get('card_number')
        branch = data.get('branch')
        greenAPI = API.GreenApi(instance_id, token)
        message = 'Ваш заказ готов, можете забрать!'
        customer_requests = CustomerRequest.objects.filter(
            card_number=card_number, branch=branch, status=1)
        for customer_request in customer_requests:
            greenAPI.sending.sendMessage(f'{customer_request.customer.phone_number}@c.us', message)
            customer_request.status = 2
            customer_request.datetime = timezone.now()
            customer_request.save()
    except Exception as e:
        capture_exception(e)
        logger.error(f"Error: {e}")

