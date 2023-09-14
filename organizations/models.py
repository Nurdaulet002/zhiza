import random
import string
from django.db import models

from accounts.models import CustomUser
from constants import BRANCH_STATUS, NOT_ACTIVE, RATE_CHOICES, RATE_DEFAULT


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
    code = models.CharField(max_length=6, unique=True, null=True, blank=True)
    rate = models.PositiveSmallIntegerField(choices=RATE_CHOICES, default=RATE_DEFAULT)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Если это новый экземпляр и код не задан
        if not self.pk and not self.code:
            self.code = self.generate_unique_code()
        super(Branch, self).save(*args, **kwargs)

    def generate_unique_code(self):
        code = self.generate_code()
        while Branch.objects.filter(code=code).exists():
            code = self.generate_code()
        return code

    @staticmethod
    def generate_code(length=6):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


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


