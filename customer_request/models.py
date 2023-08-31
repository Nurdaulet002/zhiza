from django.db import models
from constants import STATUS_WAITING, STATUS_CHOICES
from customers.models import Customer
from organizations.models import Branch


class CustomerRequest(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    card_number = models.PositiveIntegerField()
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=STATUS_WAITING)
    datetime = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'Клиент: {self.customer.phone_number} Статус: {self.status}'
