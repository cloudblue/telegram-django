import warnings

from django.apps import AppConfig  # pragma: no cover
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from django_telegram.bot.constants import (
    SETTINGS_COMMANDS_SUFFIX, SETTINGS_CONVERSATIONS,
    SETTINGS_HISTORY_LOOKUP_MODEL_PROPERTY, SETTINGS_TOKEN,
)


class TelegramBotConfig(AppConfig):  # pragma: no cover
    name = 'django_telegram.bot'
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
        settings_keys = telegram_settings.keys()
        if SETTINGS_TOKEN not in settings_keys:
            raise ImproperlyConfigured(
                f"{SETTINGS_TOKEN} key has not been set.",
            )
        if not telegram_settings[SETTINGS_TOKEN]:
            raise ImproperlyConfigured(
                f"{SETTINGS_TOKEN} key has no value set.",
            )
        if SETTINGS_COMMANDS_SUFFIX not in settings_keys:
            raise ImproperlyConfigured(
                f"{SETTINGS_COMMANDS_SUFFIX} key has not been set.",
            )
        if SETTINGS_HISTORY_LOOKUP_MODEL_PROPERTY not in settings_keys:
            raise ImproperlyConfigured(
                f"{SETTINGS_HISTORY_LOOKUP_MODEL_PROPERTY} key has not been set.",
            )
        if not telegram_settings[SETTINGS_HISTORY_LOOKUP_MODEL_PROPERTY]:
            raise ImproperlyConfigured(
                f"{SETTINGS_HISTORY_LOOKUP_MODEL_PROPERTY} key has no value set.",
            )
        if SETTINGS_CONVERSATIONS not in settings_keys:
            raise ImproperlyConfigured(
                f"{SETTINGS_CONVERSATIONS} key has not been set.",
            )
        if not isinstance(telegram_settings[SETTINGS_CONVERSATIONS], list):
            raise ImproperlyConfigured(
                f"{SETTINGS_CONVERSATIONS} must be a list of strings.",
            )

        if len(telegram_settings[SETTINGS_CONVERSATIONS]) == 0:
            warnings.warn(
                'Conversations list is empty, nothing will be setup for Telegram',
            )
