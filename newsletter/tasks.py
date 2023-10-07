import requests
import base64
import json

from customers.models import Customer

import logging

from newsletter.models import Broadcast
from organizations.models import CompanyUser

logger = logging.getLogger(__name__)



def my_scheduled_job(newsletter, token):

    customers = Customer.objects.all().select_related('branch')  # Optimized DB query

    message = newsletter.text

    for branchnewsletter in newsletter.branches.all():
        relevant_customers = [customer for customer in customers if customer.branch == branchnewsletter.branch]
        for customer in relevant_customers:
            if newsletter.image:
                file_path = newsletter.image.path
                filename = file_path.split('\\')[-1]
                with open(file_path, "rb") as image_file:
                    base64_encoded = base64.b64encode(image_file.read()).decode('utf-8')
                    url = "https://gate.whapi.cloud/messages/image"

                    payload = {
                        "media": f"data:image/png;name={filename};base64,{base64_encoded}",
                        "to": f"{customer.phone_number}@s.whatsapp.net",
                        "caption": f"{message}"
                    }
                    headers = {
                        "accept": "application/json",
                        "content-type": "application/json",
                        "authorization": f"Bearer {token}"
                    }

                    requests.post(url, json=payload, headers=headers)
                Broadcast.objects.create(newsletter=newsletter, customer=customer, message_sent=True)
            elif message:
                BASE_URL = 'https://gate.whapi.cloud/'
                data = {
                    'to': f'{customer.phone_number}@s.whatsapp.net',
                    'body': message,
                    'typing_time': 0,
                    'view_once': True,
                }

                headers = {
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }

                requests.post(f'{BASE_URL}messages/text', data=json.dumps(data), headers=headers)
                Broadcast.objects.create(newsletter=newsletter, customer=customer, message_sent=True)
    newsletter.status = 6
    newsletter.save()
