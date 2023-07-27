from django import template
from datetime import timedelta
from django.utils import timezone
from customer_request.models import CustomerRequest
from organizations.models import Branch

register = template.Library()


@register.simple_tag
def get_actual_card_color(card_number, branch_id):
    branch = Branch.objects.get(id=branch_id)
    requests = CustomerRequest.objects.filter(card_number=card_number, branch=branch, is_active=True, status=1)
    if requests:
        return 'waiting-status-color'
    else:
        return 'sent-status-color'
