from django.contrib.auth.models import AbstractUser
from django.db import models

from constants import USER_ROLE_CHOICES, USERTYPE_EMPLOYEE


class CustomUser(AbstractUser):
    """
    Расширенная пользовательская модель
    """
    role = models.PositiveSmallIntegerField(choices=USER_ROLE_CHOICES, default=USERTYPE_EMPLOYEE)
    branch = models.ForeignKey('organizations.Branch', on_delete=models.CASCADE, null=True, blank=True)
