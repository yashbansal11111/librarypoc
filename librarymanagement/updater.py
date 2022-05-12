from apscheduler.schedulers.background import BackgroundScheduler
from .jobs import checkinitialstaff, checkinitialstudent

def start():
    """This is a scheduler function which runs
    after interval of time specified below in function definition"""
    scheduler = BackgroundScheduler()
    scheduler.add_job(checkinitialstaff, trigger='interval', seconds = 2)
    scheduler.add_job(checkinitialstudent, trigger='interval', seconds = 2)
    scheduler.start()
    