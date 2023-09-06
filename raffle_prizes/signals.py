import random
import string
from whatsapp_api_client_python import API as API

from django.db.models.signals import post_save
from django.dispatch import receiver

from integrations.models import Integration
from newsletter.apscheduler import schedule_my_job
from raffle_prizes.apscheduler import schedule_send_winner_message
from raffle_prizes.models import Winner, PromoCode


@receiver(post_save, sender=Winner)
def my_model_post_save(sender, instance, created, **kwargs):
    integration = Integration.objects.get(branch=instance.customer.branch)
    ID_INSTANCE = integration.instance_id
    API_TOKEN_INSTANCE = integration.token
    greenAPI = API.GreenApi(ID_INSTANCE, API_TOKEN_INSTANCE)
    if created:
        characters = string.ascii_lowercase + string.digits

        while True:
            # Выбираем 6 случайных символов
            random_selection = ''.join(random.choice(characters) for _ in range(6))

            # Проверяем наличие промокода в базе данных
            if not PromoCode.objects.filter(promo_code=random_selection).exists():
                promo_code = PromoCode.objects.create(promo_code=random_selection, raffle_prize=instance.raffle_prize, customer=instance.customer)
                message = instance.raffle_prize.message_winner + f'\n Вам промо код - {promo_code.promo_code}'
                if instance.raffle_prize.image:
                    data = {
                        'phone_number': instance.customer.phone_number,
                        'message': message,
                        'file_path': instance.raffle_prize.image.path
                    }
                else:
                    data = {
                        'phone_number': instance.customer.phone_number,
                        'message': message
                    }
                schedule_send_winner_message(data=data)
                break


