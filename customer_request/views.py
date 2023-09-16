import json
from datetime import datetime, timedelta

from django.utils.timezone import now
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic.base import View, TemplateResponseMixin
from django.views.generic import ListView
from whatsapp_api_client_python import API as API

from customers.models import Customer
from feedback.models import Rating
from integrations.models import Integration
from organizations.models import Branch
from .models import CustomerRequest


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
        integration = Integration.objects.get(branch=self.request.user.branch)
        greenAPI = API.GreenApi(integration.instance_id, integration.token)
        message = 'Ваш заказ готов! Забирайте в течений 15 минут!'
        card_number = request.POST.get('card_number')
        customer_requests = CustomerRequest.objects.filter(
            card_number=card_number, branch=request.user.branch, status=1)
        for customer_request in customer_requests:
            greenAPI.sending.sendMessage(f'{customer_request.customer.phone_number}@c.us', message)
            customer_request.status = 2
            customer_request.datetime = timezone.now()
            customer_request.save()
        return JsonResponse({'data': {}})


@csrf_exempt
@require_POST
def webhookWhatsApp(request):
    data = json.loads(request.body)
    type_webhook = data.get('typeWebhook')
    if type_webhook == 'incomingMessageReceived':
        print(data)
        process_incoming_message(data)
    return HttpResponse(status=200)


def process_incoming_message(data):
    instance_id = data['instanceData']['idInstance']
    integration = Integration.objects.get(instance_id=instance_id)
    greenAPI = API.GreenApi(integration.instance_id, integration.token)
    phone_number = data['senderData']['chatId'][:11]

    message_data = data.get('messageData', {})
    type_message = message_data.get('typeMessage')
    text_message_data = message_data.get('textMessageData', {})

    # if type_message == 'textMessage':
    #     card_number = text_message_data.get('textMessage')

    # message_data = data.get('messageData', {})
    # type_message = message_data.get('typeMessage')
    # text_message_data = message_data.get('extendedTextMessageData', {})

    if type_message == 'textMessage':
        card_number = text_message_data.get('textMessage')
        print(card_number)
        if len(card_number) >= 6:
            try:
                branch_code = card_number[0:6]
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
        # Если нет последнего запроса клиента, добавьте логику для обработки этой ситуации

        card_number = get_card_number_choice(card_number)

        if card_number != 'Not Card Number':

            customer, created = Customer.objects.get_or_create(phone_number=phone_number, branch=branch)
            customer_request = get_active_customer_request(customer, branch)

            if customer_request:
                message = f'Вы уже оставили запрос! Мы сообщим вам, когда ваш заказ будет готов!'
                greenAPI.sending.sendMessage(f'{phone_number}@c.us', message)
                return
            else:
                create_customer_request(customer, card_number, branch)
                group_manager = 'whatsapp_socket_%s' % branch.id
                send_group_message(group_manager, card_number)
                message = f'Отлично! Мы сообщим вам, когда ваш заказ будет готов!'
                greenAPI.sending.sendMessage(f'{phone_number}@c.us', message)
                return

        else:
            customer, created = Customer.objects.get_or_create(phone_number=phone_number, branch=branch)
            customer_request = get_active_customer_request(customer, branch)
            if customer_request:
                process_customer_rating(greenAPI, customer_request, text_message_data.get('text'))
            else:
                return

    else:
        # Действия, выполняемые в случае, если type_message не является 'textMessage'
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



def process_customer_rating(greenAPI, customer_request, text_message):
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
            send_feedback_confirmation(greenAPI, customer_request.customer.phone_number)
    except Rating.DoesNotExist:
        if text_message.isdigit():
            text_message = int(text_message)
            if text_message in range(1, 4):
                send_rating_feedback(greenAPI, customer_request.customer.phone_number)
                Rating.objects.create(customer_request=customer_request, rating=text_message)
            elif text_message in range(4, 6):
                send_positive_feedback(greenAPI, customer_request.customer.phone_number, customer_request.branch.address)
                Rating.objects.create(customer_request=customer_request, rating=text_message)
                customer_request.is_active = False
                customer_request.save()
        else:
            send_invalid_rating_message(greenAPI, customer_request.customer.phone_number)



def send_rating_feedback(greenAPI, phone_number):
    message = '''Можете в 20 словах кратко описать, почему вам не понравился наш продукт! Пишите все в одну строку!'''
    result = greenAPI.sending.sendMessage(f'{phone_number}@c.us', message)
    return JsonResponse({'data': result.data})


def send_positive_feedback(greenAPI, phone_number, address):
    message = f'Спасибо, что выбрали нас! Мы рады, что вам нравится наш продукт. Можете оставить отзыв в 2 ГИС {address}'
    result = greenAPI.sending.sendMessage(f'{phone_number}@c.us', message)
    return JsonResponse({'data': result.data})


def send_invalid_rating_message(greenAPI, phone_number):
    message = '''Вы ввели неверную информацию! Отправьте только цифру!!!'''
    result = greenAPI.sending.sendMessage(f'{phone_number}@c.us', message)
    return JsonResponse({'data': result.data})


def send_feedback_confirmation(greenAPI, phone_number):
    message = '''Спасибо за ваш отзыв! Ваш отзыв обязательно будет учтен!'''
    result = greenAPI.sending.sendMessage(f'{phone_number}@c.us', message)
    return JsonResponse({'data': result.data})


def get_card_number_choice(card_number):
    card_number = card_number[8:]
    if card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер карточки - 1':
        return 1
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер карточки - 2':
        return 2
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер карточки - 3':
        return 3
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер карточки - 4':
        return 4
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер карточки - 5':
        return 5
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер карточки - 6':
        return 6
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер карточки - 7':
        return 7
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер карточки - 8':
        return 8
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер карточки - 9':
        return 9
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер карточки - 10':
        return 10
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер карточки - 11':
        return 11
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер карточки - 12':
        return 12
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер карточки - 13':
        return 13
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер карточки - 14':
        return 14
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер карточки - 15':
        return 15
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер карточки - 16':
        return 16
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер карточки - 17':
        return 17
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер карточки - 18':
        return 18
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер карточки - 19':
        return 19
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер карточки - 20':
        return 20
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер карточки - 21':
        return 21
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер карточки - 22':
        return 22
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер карточки - 23':
        return 23
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер карточки - 24':
        return 24
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер карточки - 25':
        return 25
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер карточки - 26':
        return 26
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер карточки - 27':
        return 27
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер карточки - 28':
        return 28
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер карточки - 29':
        return 29
    elif card_number == 'Хочу получить уведомление, когда заказ будет готов. Номер карточки - 30':
        return 30
    else:
        return 'Not Card Number'