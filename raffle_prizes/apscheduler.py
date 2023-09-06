from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from raffle_prizes.tasks import task_send_winner_message

scheduler = BackgroundScheduler()
scheduler.start()


def schedule_send_winner_message(data):
    run_date = datetime.now()
    scheduler.add_job(task_send_winner_message, 'date', run_date=run_date, args=[data])


