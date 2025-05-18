from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from .kafka.producer import send_rss_channels_to_kafka
from .kafka.consumer import consume_feed
import threading

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(
        send_rss_channels_to_kafka,
        IntervalTrigger(minutes=1),
    )

def start_kafka_consumer():
    threading.Thread(target=consume_feed, daemon=True).start()