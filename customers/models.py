from django.db import models
from organizations.models import Branch

class Customer(models.Model):
    phone_number = models.CharField(max_length=15)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Филиал: {self.branch} / Номер телефона: {self.phone_number}'
