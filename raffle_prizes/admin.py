from django.contrib import admin

from raffle_prizes.models import RafflePrize, ParticipatingBranch, Winner, PromoCode, CheckingCode

admin.site.register(RafflePrize)
admin.site.register(ParticipatingBranch)
admin.site.register(Winner)
admin.site.register(PromoCode)
admin.site.register(CheckingCode)
