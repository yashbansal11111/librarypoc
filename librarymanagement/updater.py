from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .jobs import checkinitial

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(checkinitial, trigger='interval', seconds = 2)
    scheduler.start()