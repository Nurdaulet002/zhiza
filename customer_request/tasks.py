
from whatsapp_api_client_python import API as API
from django.http import JsonResponse

from integrations.models import Integration


def my_scheduled_job(phone_number, instance_id, token):
    greenAPI = API.GreenApi(instance_id, token)
    message = '''Оцените по  5 балльной шкале: 
        1 - Ужасно
        2 - Очень плохо
        3 - Плохо
        4 - Хорошо
        5 - Отлично
        !!! Отправьте только одну цифру !!!'''
    result = greenAPI.sending.sendMessage(f'{phone_number}@c.us', message)
    print("Job is running...")
    return JsonResponse({'data': result.data})


