from django.db import models




class Integration(models.Model):
    phone_number = models.CharField(max_length=300, null=True, blank=True)
    instance_id = models.CharField(max_length=300)
    token = models.CharField(max_length=300)
    date_from = models.DateField()
    date_to = models.DateField()


