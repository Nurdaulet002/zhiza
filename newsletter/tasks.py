from os.path import basename
from urllib.parse import urlparse
from sentry_sdk import capture_exception
from whatsapp_api_client_python import API as API
from django.http import JsonResponse

from customers.models import Customer

import logging

logger = logging.getLogger(__name__)
ID_INSTANCE = '1101817797'
API_TOKEN_INSTANCE = '444b8de1fd9d4c38a1cf4df0a43770b924f64bf46db349ac95'

class GreenAPIService:
    def __init__(self):
        self.api = API.GreenApi(ID_INSTANCE, API_TOKEN_INSTANCE)

    def send_message(self, phone_number, message):
        try:
            self.api.sending.sendMessage(f'{phone_number}@c.us', message)
        except Exception as e:
            capture_exception(e)
            logger.error(f"Error sending message to {phone_number}: {e}")

    def send_file(self, phone_number, file_path, message):
        try:
            upload_response = self.api.sending.uploadFile(file_path)
            if upload_response.code == 200:
                url_file = upload_response.data["urlFile"]
                file_name = basename(urlparse(url_file).path)
                self.api.sending.sendFileByUrl(f"{phone_number}@c.us", url_file, file_name, message)
            else:
                error_message = upload_response.data.get("errorMessage", "Unknown error")
                logger.warning(f"Failed to upload file for {phone_number}. Status code: {upload_response.code}. Error message: {error_message}")
        except Exception as e:
            capture_exception(e)
            logger.error(f"Error sending file to {phone_number}: {e}")



def my_scheduled_job(newsletter):
    green_api_service = GreenAPIService()
    customers = Customer.objects.all().select_related('branch')  # Optimized DB query

    message = newsletter.text

    for branchnewsletter in newsletter.branches.all():
        relevant_customers = [customer for customer in customers if customer.branch == branchnewsletter.branch]
        for customer in relevant_customers:
            if newsletter.image:
                green_api_service.send_file(customer.phone_number, newsletter.image.path, message)
            elif message:
                green_api_service.send_message(customer.phone_number, message)

    newsletter.status = 6
    newsletter.save()
