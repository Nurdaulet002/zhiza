from django.db import models
from customers.models import Customer
from shop.models import Shop

STATUS_WAITING = 1
STATUS_SENT = 2
USERTYPE_DEFAULT = STATUS_WAITING

class CustomerRequest(models.Model):
    STATUS_CHOICES = (
        (STATUS_WAITING, 'waiting'),
        (STATUS_SENT, 'sent'),
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    card_number = models.PositiveIntegerField()
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=STATUS_WAITING)

    def __str__(self):
        return f'Клиент: {self.customer.phone_number} Статус: {self.status}'



