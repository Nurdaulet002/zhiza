from django.contrib import admin
from newsletter.models import Newsletter, BranchNewsletter


admin.site.register(Newsletter)
admin.site.register(BranchNewsletter)
# Register your models here.
