from django.db import models
from customer_request.models import CustomerRequest

class Rating(models.Model):
    customer_request = models.OneToOneField(CustomerRequest, on_delete=models.CASCADE, related_name='rating')
    rating = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'{self.customer_request} {self.rating}'


class Review(models.Model):
    rating = models.OneToOneField(Rating, on_delete=models.CASCADE, related_name='review')
    text = models.TextField()

    def __str__(self):
        return f'{self.rating.rating} {self.text}'
