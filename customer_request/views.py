import json
import requests

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic.base import View, TemplateResponseMixin

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from customers.models import Customer
from feedback.models import Rating
from integrations.models import Integration
from organizations.models import Branch

from .models import CustomerRequest
from .tasks import task_send_message_order_completed


class EmployeeIndexView(TemplateResponseMixin, View):
    template_name = 'customer_request/employee_index.html'

    def get(self, request, *args, **kwargs):
        branch = self.request.user.branch.id
        cards = self.request.user.branch.cards_number
        context = {
            'cards': range(1, cards + 1),
            'branch': branch,
        }
        return self.render_to_response(context)


class SendMessageView(View):

    def post(self, request, *args, **kwargs):
        integration = Integration.objects.get(id=self.request.user.branch.integration.id)
        card_number = request.POST.get('card_number')
        branch = request.user.branch
        data = {
            'token': integration.token,
            'card_number': card_number,
            'branch': branch
        }
        task_send_message_order_completed(data=data)
        return JsonResponse({'data': {}})


@csrf_exempt
@require_POST
def webhookWhatsApp(request):
    data = json.loads(request.body)
    if 'messages' in data:
        first_message = data['messages'][0]
        if not first_message['from_me']:
            process_incoming_message(data)
    return HttpResponse(status=200)

def send_message_whapi(token, phone_number, message):
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

    response = requests.post(f'{BASE_URL}messages/text', data=json.dumps(data), headers=headers)

    return JsonResponse(response.json())


def process_incoming_message(data):
    phone_number = data['messages'][0]['chat_id'].split('@')[0]
    card_number = data['messages'][0]['text']['body']

    if len(card_number) >= 6:
        try:
            branch_code = card_number[69:75]
            branch = Branch.objects.get(code=branch_code)
        except ObjectDoesNotExist:
            last_customer_request = CustomerRequest.objects.filter(customer__phone_number=phone_number,
                                                                   is_active=True).last()
            if last_customer_request:
                branch = last_customer_request.branch
            else:
                return
    else:
        last_customer_request = CustomerRequest.objects.filter(customer__phone_number=phone_number).last()
        if last_customer_request:
            branch = last_customer_request.branch
        else:
            return

    card_number = get_card_number_choice(card_number)

    if card_number != 'Not Card Number':
        customer, created = Customer.objects.get_or_create(phone_number=phone_number, branch=branch)
        customer_request = get_active_customer_request(customer, branch)

        if customer_request:
            message = f'Вы уже оставили запрос! Мы сообщим вам, когда ваш заказ будет готов.'
            send_message_whapi(branch.integration.token, phone_number, message)
            return
        else:
            create_customer_request(customer, card_number, branch)
            group_manager = f'whatsapp_socket_{branch.id}'
            send_group_message(group_manager, card_number)
            message = f'Отлично! Мы сообщим вам, когда ваш заказ будет готов.'
            send_message_whapi(branch.integration.token, phone_number, message)
            return
    else:
        customer, created = Customer.objects.get_or_create(phone_number=phone_number, branch=branch)
        customer_request = get_active_customer_request(customer, branch)
        if customer_request:
            process_customer_rating(branch.integration.token, customer_request, data['messages'][0]['text']['body'])
        else:
            return


#Получить актуальную CustomerRequest
def get_active_customer_request(customer, branch):
    try:
        return CustomerRequest.objects.get(
            branch=branch,
            is_active=True,
            customer=customer
        )
    except CustomerRequest.DoesNotExist:
        return None

#Создать новый CustomerRequest
def create_customer_request(customer, card_number, branch):
    return CustomerRequest.objects.create(
        customer=customer,
        branch=branch,
        card_number=card_number,
        datetime=timezone.now(),
        is_active=True
    )

#Показать асинхронно CustomerRequest в html
def send_group_message(group_manager, card_number):
    channel_layer = get_channel_layer()
    data = {
        'type': 'whatsapp_socket',
        'card_number': card_number
    }
    async_to_sync(channel_layer.group_send)(group_manager, data)



def process_customer_rating(token, customer_request, text_message):
    if customer_request.status == 1:
        return
    try:
        rating = Rating.objects.get(customer_request=customer_request)
        if rating.comment:
            customer_request.is_active = False
            customer_request.save()
        else:
            rating.comment = str(text_message)
            rating.save()
            customer_request.is_active = False
            customer_request.save()
            send_feedback_confirmation(token, customer_request.customer.phone_number)
    except Rating.DoesNotExist:
        if text_message.isdigit():
            text_message = int(text_message)
            if text_message in range(1, 4):
                send_rating_feedback(token, customer_request.customer.phone_number)
                Rating.objects.create(customer_request=customer_request, rating=text_message)
            elif text_message in range(4, 6):
                send_positive_feedback(token, customer_request.customer.phone_number, customer_request.branch.address)
                Rating.objects.create(customer_request=customer_request, rating=text_message)
                customer_request.is_active = False
                customer_request.save()
        else:
            send_invalid_rating_message(token, customer_request.customer.phone_number)



def send_rating_feedback(token, phone_number):
    message = '''Не могли бы вы указать, что вам не понравилось в нашем продукте? Пожалуйста, ответьте одним сообщением!'''
    send_message_whapi(token, phone_number, message)
    return JsonResponse({})


def send_positive_feedback(token, phone_number, address):
    message = f'Благодарим за ваш выбор! Надеемся, что наш продукт удовлетворил ваши ожидания. Будем признательны за ваш отзыв в 2 ГИС {address}'
    result = send_message_whapi(token, phone_number, message)
    return JsonResponse({})


def send_invalid_rating_message(token, phone_number):
    message = '''Похоже, была введена неверная информация. Пожалуйста, отправьте только цифровое значение!'''
    result = send_message_whapi(token, phone_number, message)
    return JsonResponse({})


def send_feedback_confirmation(token, phone_number):
    message = '''Благодарим за ваше мнение! Мы обязательно учтем ваш отзыв.'''
    result = send_message_whapi(token, phone_number, message)
    return JsonResponse({})


def get_card_number_choice(card_number):
    card_number = card_number[0:68]
    print(card_number)
    if card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер заказа: 01':
        return 1
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер заказа: 02':
        return 2
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер заказа: 03':
        return 3
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер заказа: 04':
        return 4
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер заказа: 05':
        return 5
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер заказа: 06':
        return 6
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер заказа: 07':
        return 7
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер заказа: 08':
        return 8
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер заказа: 09':
        return 9
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер заказа: 10':
        return 10
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер заказа: 11':
        return 11
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер заказа: 12':
        return 12
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер заказа: 13':
        return 13
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер заказа: 14':
        return 14
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер заказа: 15':
        return 15
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер заказа: 16':
        return 16
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер заказа: 17':
        return 17
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер заказа: 18':
        return 18
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер заказа: 19':
        return 19
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер заказа: 20':
        return 20
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер заказа: 21':
        return 21
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер заказа: 22':
        return 22
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер заказа: 23':
        return 23
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер заказа: 24':
        return 24
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер заказа: 25':
        return 25
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер заказа: 26':
        return 26
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер заказа: 27':
        return 27
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер заказа: 28':
        return 28
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер заказа: 29':
        return 29
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер заказа: 30':
        return 30
    else:
        return 'Not Card Number'