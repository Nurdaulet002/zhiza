from django import template

from accounts.models import CustomUser
from customers.models import Customer
from newsletter.models import Newsletter, BranchNewsletter
from organizations.models import CompanyUser

register = template.Library()


@register.simple_tag
def get_count_customers_number(newsletter_id):
    newsletter = Newsletter.objects.get(id=newsletter_id)
    branch_newsletter_count = BranchNewsletter.objects.filter(newsletter=newsletter).count()
    if branch_newsletter_count:
        return branch_newsletter_count
    else:
        return 'Еще не добавлена! (0)'

@register.simple_tag
def get_user_branch_list(user_id):
    user = CustomUser.objects.get(id=user_id)
    company_user = CompanyUser.objects.get(user=user)
    branches = company_user.company.branches.all()
    return branches

@register.simple_tag
def get_customers_count(newsletter_id):
    count = 0
    newsletter = Newsletter.objects.get(id=newsletter_id)
    branch_newsletters = BranchNewsletter.objects.filter(newsletter=newsletter)
    customers = Customer.objects.all()
    for branch_newsletter in branch_newsletters:
        for customer in customers:
            if customer.branch == branch_newsletter.branch:
                count += 1
    return f'Количество получатели {count}'


@register.filter(name='filename')
def filename(value):
    return value.split("/")[-1]
