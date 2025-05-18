from django.apps import AppConfig


class FeedWatcherConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'feed_watcher'

    def ready(self):
        from .scheduler import start_scheduler, start_kafka_consumer
        start_scheduler()
        start_kafka_consumer()
