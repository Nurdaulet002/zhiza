from whatsapp_api_client_python import API as API
from django.http import JsonResponse

from customers.models import Customer


def my_scheduled_job(newsletter):
    ID_INSTANCE = '1101817774'
    API_TOKEN_INSTANCE = 'ecad3cbbda704ea0ab0f1a784f527c06938cf64fb3924895a0'
    greenAPI = API.GreenApi(ID_INSTANCE, API_TOKEN_INSTANCE)
    customers = Customer.objects.all()
    message = newsletter.text
    image_name = str(newsletter.image)
    image_name = image_name[19:]
    for branchnewsletter in newsletter.branches.all():
        for customer in customers:
            if customer.branch == branchnewsletter.branch:
                greenAPI.sending.sendFileByUpload(
                    f"{customer.phone_number}@c.us",
                    newsletter.image.path,
                    image_name,
                    message
                )
    newsletter.status = 6
    newsletter.save()
    return JsonResponse({})