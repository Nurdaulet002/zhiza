from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from .tasks import my_scheduled_job

scheduler = BackgroundScheduler()
scheduler.start()

def schedule_my_job(phone_number):
    run_date = datetime.now() + timedelta(seconds=10)
    scheduler.add_job(my_scheduled_job, 'date', run_date=run_date, args=[phone_number])


