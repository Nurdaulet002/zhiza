from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from newsletter.tasks import my_scheduled_job

scheduler = BackgroundScheduler()
scheduler.start()

def schedule_my_job(newsletter):
    print('newsletter is', newsletter)
    run_date = datetime.now() + timedelta(seconds=2)
    scheduler.add_job(my_scheduled_job, 'date', run_date=run_date, args=[newsletter])


