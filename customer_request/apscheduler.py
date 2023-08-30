from datetime import datetime, timedelta
from whatsapp_api_client_python import API as API
from apscheduler.schedulers.background import BackgroundScheduler

from feedback.models import Rating
from customer_request.models import CustomerRequest
from .tasks import my_scheduled_job


def get_or_create_scheduler():
    global scheduler
    if 'scheduler' not in globals():
        scheduler = BackgroundScheduler()
        scheduler.start()
    return scheduler


def schedule_my_job(phone_number):
    scheduler = get_or_create_scheduler()
    run_date = datetime.now() + timedelta(seconds=10)
    scheduler.add_job(my_scheduled_job, 'date', run_date=run_date, args=[phone_number])


def check_requests_without_ratings_after_60_minutes():
    now = datetime.now()
    sixty_minutes_ago = now - timedelta(minutes=60)

    # Получаем все запросы, которые были созданы более 60 минут назад, но у которых еще нет оценки.
    requests_without_ratings = CustomerRequest.objects.filter(
        datetime__lte=sixty_minutes_ago, is_active=True
    ).exclude(
        id__in=Rating.objects.values_list('customer_request_id', flat=True)
    )

    for request in requests_without_ratings:
        request.is_active = False
        request.save()


def update_messages_without_rating():
    scheduler = get_or_create_scheduler()
    scheduler.add_job(check_requests_without_ratings_after_60_minutes, 'interval', minutes=5)


