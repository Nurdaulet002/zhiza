from django.contrib.auth.models import AbstractUser
from django.db import models

class Company(models.Model):
    title = models.CharField(max_length=180)

    def __str__(self):
        return self.title

USERTYPE_OWNER = 1
USERTYPE_MANAGER = 2
USERTYPE_EMPLOYEE = 3
USERTYPE_DEFAULT = USERTYPE_EMPLOYEE


class CustomUser(AbstractUser):
    """Расширенная пользовательская модель"""
    USER_ROLE_CHOICES = (
        (USERTYPE_OWNER, 'owner'),
        (USERTYPE_MANAGER, 'manager'),
        (USERTYPE_EMPLOYEE, 'employee'),
    )
    role = models.PositiveSmallIntegerField(choices=USER_ROLE_CHOICES, default=USERTYPE_EMPLOYEE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.username