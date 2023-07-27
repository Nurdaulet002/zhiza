from django.contrib import admin

from organizations.models import Branch, Company, CompanyUser

admin.site.register(Branch)
admin.site.register(Company)
admin.site.register(CompanyUser)
