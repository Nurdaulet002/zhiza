from django.db.models.signals import post_save
from django.dispatch import receiver

from customer_request.apscheduler import schedule_my_job
from customer_request.models import CustomerRequest


@receiver(post_save, sender=CustomerRequest)
def my_model_post_save(sender, instance, created, **kwargs):
    if created:
        pass
    else:
        if instance.is_active:
            schedule_my_job(phone_number=instance.customer.phone_number,
                            token=instance.branch.integration.token)
        else:
            pass
