from django import template
from django.db.models import Avg, Count
from datetime import datetime, timedelta
from django.utils import timezone

from customer_request.models import CustomerRequest
from customers.models import Customer
from feedback.models import Rating
from organizations.models import Branch

register = template.Library()


@register.simple_tag
def get_branches_list_by_user(branches, user_branch):
    branch_list = []
    for branch in branches:
        if branch == user_branch:
            branch_list.append(branch)
    return branch_list


@register.simple_tag
def get_avg_rating(branch_id):
    branch = Branch.objects.get(id=branch_id)
    customer_requests = CustomerRequest.objects.filter(branch=branch)
    average_rating = customer_requests.aggregate(Avg('rating__rating'))['rating__rating__avg']
    return  average_rating


@register.simple_tag
def get_count_rating_with_comment(branch_id):
    branch = Branch.objects.get(id=branch_id)
    customer_requests_with_comment = CustomerRequest.objects.filter(branch=branch, rating__comment__isnull=False)
    num_ratings_with_comment = customer_requests_with_comment.count()
    return num_ratings_with_comment


@register.simple_tag
def get_count_customers(branch_id):
    branch = Branch.objects.get(id=branch_id)
    customers = Customer.objects.filter(branch=branch)
    num_customers = customers.count()
    return num_customers


@register.simple_tag
def get_count_customer_requests(branch_id):
    branch = Branch.objects.get(id=branch_id)
    customer_requests = CustomerRequest.objects.filter(branch=branch)
    num_customer_requests = customer_requests.count()
    return num_customer_requests


@register.simple_tag
def get_pf(branch_id):
    branch = Branch.objects.get(id=branch_id)
    num_customer_requests = CustomerRequest.objects.filter(branch=branch).count()
    unique_customer_requests_count = CustomerRequest.objects.values('customer').annotate(
        request_count=Count('customer')).filter(request_count=1, branch=branch).count()
    pf = num_customer_requests / unique_customer_requests_count
    return pf


@register.simple_tag
def get_rpr(branch_id):
    branch = Branch.objects.get(id=branch_id)
    num_customer_requests = CustomerRequest.objects.filter(branch=branch).count()
    customer_requests_count  = CustomerRequest.objects.values('customer').annotate(
        request_count=Count('customer')).filter(request_count__gt=1, branch=branch).count()
    rpr = customer_requests_count / num_customer_requests
    return round(rpr, 2)


@register.simple_tag
def get_customers_created_month_ago(branch_id):
    branch = Branch.objects.get(id=branch_id)
    current_datetime = timezone.now()
    one_month_ago = current_datetime - timedelta(days=30)
    recent_customers = Customer.objects.filter(created_at__gte=one_month_ago, branch=branch).count()
    return recent_customers

@register.simple_tag
def get_customers_purchase_only_once(branch_id):
    branch = Branch.objects.get(id=branch_id)
    unique_customer_requests_count = CustomerRequest.objects.values('customer').annotate(
        request_count=Count('customer')).filter(request_count=1, branch=branch).count()
    return unique_customer_requests_count


@register.simple_tag
def get_customers_purchase_more_than_one(branch_id):
    branch = Branch.objects.get(id=branch_id)
    customer_requests_count = CustomerRequest.objects.values('customer').annotate(
        request_count=Count('customer')).filter(request_count__gt=1, branch=branch).count()
    return customer_requests_count

@register.simple_tag
def get_rating_with_number(branch_id, number):
    ratings = Rating.objects.filter(customer_request__branch_id=branch_id, rating=number)
    rating_count = ratings.count()
    return rating_count


