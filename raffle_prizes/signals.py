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
    if created:
        characters = string.ascii_lowercase + string.digits

        while True:
            # Выбираем 6 случайных символов
            random_selection = ''.join(random.choice(characters) for _ in range(6))

            # Проверяем наличие промокода в базе данных
            if not PromoCode.objects.filter(promo_code=random_selection).exists():
                promo_code = PromoCode.objects.create(promo_code=random_selection, winner=instance)
                message = instance.raffle_prize.message_winner + f'\nВаш промо код - {promo_code.promo_code}'
                if instance.raffle_prize.image:
                    data = {
                        'phone_number': instance.customer.phone_number,
                        'message': message,
                        'file_path': instance.raffle_prize.image.path,
                        'instance_id': instance.customer.branch.integration.instance_id,
                        'token': instance.customer.branch.integration.token
                    }
                else:
                    data = {
                        'phone_number': instance.customer.phone_number,
                        'message': message,
                        'instance_id': instance.customer.branch.integration.instance_id,
                        'token': instance.customer.branch.integration.token
                    }
                schedule_send_winner_message(data=data)
                break


