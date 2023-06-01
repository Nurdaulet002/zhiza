from django.db import models
from accounts.models import Company

class Shop(models.Model):
    title = models.CharField(max_length=180)
    cards_number = models.PositiveIntegerField()

    def __str__(self):
        return self.title

class CompanyShop(models.Model):
    company = models.ManyToManyField(Company)
    shop = models.ManyToManyField(Shop)
