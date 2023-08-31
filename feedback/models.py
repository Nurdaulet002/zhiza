from django.db import models
from customer_request.models import CustomerRequest

class Rating(models.Model):
    customer_request = models.OneToOneField(
        CustomerRequest, on_delete=models.CASCADE, related_name='rating')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(null=True, blank=True)
    created = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.customer_request} {self.rating}'
