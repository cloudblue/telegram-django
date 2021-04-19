from django.conf import settings

from telegram import Bot

from django_telegram.bot.constants import SETTINGS_CHAT_ID, SETTINGS_MW, SETTINGS_TOKEN


def send_message(message):
    try:
        bot = Bot(settings.TELEGRAM_BOT[SETTINGS_TOKEN])
        bot.send_message(settings.TELEGRAM_BOT[SETTINGS_MW][SETTINGS_CHAT_ID], message)
        return True
    except Exception:
        #  we do not want this to affect any operations
        return False
