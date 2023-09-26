from django.contrib import admin
from newsletter.models import Newsletter, BranchNewsletter, Broadcast


admin.site.register(Newsletter)
admin.site.register(BranchNewsletter)
admin.site.register(Broadcast)
# Register your models here.
