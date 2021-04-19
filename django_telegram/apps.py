from django.apps import AppConfig  # pragma: no cover
from django.conf import settings  # pragma: no cover
from django.core.exceptions import ImproperlyConfigured  # pragma: no cover

from django_telegram.configurator import TelegramBotConfigurator  # pragma: no cover


class TelegramBotConfig(AppConfig):  # pragma: no cover
    name = 'django_telegram'
    verbose_name = "Django Telegram Bot"

    def ready(self):
        telegram_settings = getattr(settings, 'TELEGRAM_BOT', None)
        if not telegram_settings:
            raise ImproperlyConfigured(
                "Error obtaining telegram bot settings. ",
                "Please check the documentation on how to configure settings.py ",
                "in your project. TELEGRAM_BOT object is missing.",
            )
        if not isinstance(telegram_settings, dict):
            raise ImproperlyConfigured(
                "TELEGRAM_BOT object must be a dictionary.",
            )
        checker = TelegramBotConfigurator(telegram_settings, settings.MIDDLEWARE)
        checker.run_check()
