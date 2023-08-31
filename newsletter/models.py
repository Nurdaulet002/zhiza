from django.db import models
from constants import NEWSLETTER_STATUS, STATUS_DRAFT
from organizations.models import Branch

class Newsletter(models.Model):
    title = models.CharField(max_length=180)
    text = models.TextField(null=True, blank=True)
    status = models.PositiveSmallIntegerField(choices=NEWSLETTER_STATUS, default=STATUS_DRAFT)
    total_customers = models.PositiveIntegerField(null=True, blank=True)
    total_getting_customers = models.PositiveIntegerField(null=True, blank=True)
    active_last_month = models.BooleanField(default=False)
    active_last_week = models.BooleanField(default=False)
    active_last_day = models.BooleanField(default=False)
    image = models.ImageField(upload_to='newsletter_picture/', null=True, blank=True)

    def __str__(self):
        return self.title


class BranchNewsletter(models.Model):
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE, related_name='branches')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
