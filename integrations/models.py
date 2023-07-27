from django.db import models

from organizations.models import Branch


class Integration(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    instance_id = models.CharField(max_length=300)
    token = models.CharField(max_length=300)
    date_from = models.DateField()
    date_to = models.DateField()

    def __str__(self):
        return self.branch.title
