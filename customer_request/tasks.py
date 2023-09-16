
from whatsapp_api_client_python import API as API
from django.http import JsonResponse

from integrations.models import Integration


def my_scheduled_job(phone_number):
    ID_INSTANCE = '1101817797'
    API_TOKEN_INSTANCE = '444b8de1fd9d4c38a1cf4df0a43770b924f64bf46db349ac95'
    greenAPI = API.GreenApi(ID_INSTANCE, API_TOKEN_INSTANCE)
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


