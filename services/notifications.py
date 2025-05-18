import threading
import time
from datetime import datetime

from models import *
from services.database import DataBase


def check_events_updates(bot):
    db = DataBase()
    last_check = datetime.now()

    while True:
        workshop_request: Request = db.get_workshops()

        if workshop_request.status != Status.OK:
            continue

        # Нахождение начатых воркшопах
        for workshop in workshop_request.value:
            if workshop.start >= last_check:
                notify_user(bot, workshop)
                db.set_workshop_notify(workshop.id, True)

        time.sleep(60)
        last_check = datetime.now()


def notify_user(bot, workshop: Workshop):
    users = workshop.registered_user_ids
    for user_id in users:
        try:
            bot.send_message(user_id,
                             f"🎉 Началось мероприятие: {workshop.title}\n"
                             f"📍 Место: {workshop.location}")
        except Exception:
            continue


def start_notification_service(bot):
    """Запуск в отдельном потоке"""
    thread = threading.Thread(name="thead_notification_service", target=check_events_updates, args=(bot,))
    thread.daemon = True
    thread.start()
