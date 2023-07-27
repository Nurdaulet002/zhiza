from django.db import models

from accounts.models import CustomUser


class Branch(models.Model):
    """
    Филиал
    """
    title = models.CharField(max_length=180)
    cards_number = models.PositiveIntegerField(default=10)

    def __str__(self):
        return self.title


class Company(models.Model):
    """
    Компания
    """
    title = models.CharField(max_length=180)
    branches = models.ManyToManyField(Branch)

    def __str__(self):
        return self.title


class CompanyUser(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)


