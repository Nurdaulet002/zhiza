from django.db import models

from constants import RAFFLE_PRIZE_STATUS, NOT_PLAYED
from customer_request.models import CustomerRequest
from organizations.models import Branch


class RafflePrize(models.Model):
    title = models.CharField(max_length=180)
    message_winner = models.TextField()
    number_winners = models.PositiveIntegerField(default=1)
    date_start = models.DateField()
    date_end = models.DateField()
    comment = models.TextField()
    status = models.PositiveSmallIntegerField(choices=RAFFLE_PRIZE_STATUS, default=NOT_PLAYED)

    def __str__(self):
        return self.title


class ParticipatingBranch(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    raffle_prize = models.ForeignKey(RafflePrize, on_delete=models.CASCADE)


class PromoCode(models.Model):
    raffle_prize = models.ForeignKey(RafflePrize, on_delete=models.CASCADE)
    customer_request = models.ForeignKey(CustomerRequest, on_delete=models.CASCADE)
    promo_code = models.CharField(max_length=180, unique=True)

class Winner(models.Model):
    raffle_prize = models.ForeignKey(RafflePrize, on_delete=models.CASCADE)
    customer_request = models.ForeignKey(CustomerRequest, on_delete=models.CASCADE)
    date_win = models.DateField(auto_now=True)