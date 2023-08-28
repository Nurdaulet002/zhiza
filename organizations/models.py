from django.db import models

from accounts.models import CustomUser
from constants import BRANCH_STATUS, NOT_ACTIVE


class Branch(models.Model):
    """
    Филиал
    """
    title = models.CharField(max_length=180)
    address = models.CharField(max_length=180, null=True, blank=True)
    cards_number = models.PositiveIntegerField(default=10)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.PositiveSmallIntegerField(choices=BRANCH_STATUS, default=NOT_ACTIVE)

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


