import logging

from django.utils.module_loading import import_string

from telegram import ReplyKeyboardRemove
from telegram.ext import Updater

from django.conf import settings

from django_telegram.bot.constants import LOGGER_NAME
from django_telegram.bot.constants import (
    SETTINGS_COMMANDS_SUFFIX, SETTINGS_CONVERSATIONS,
    SETTINGS_HISTORY_LOOKUP_MODEL_PROPERTY, SETTINGS_TOKEN,
)


class BotRunner(object):  # pragma: no cover

    def __init__(self):
        self.token = settings.TELEGRAM_BOT[SETTINGS_TOKEN]
        self.suffix = settings.TELEGRAM_BOT[SETTINGS_COMMANDS_SUFFIX]
        self.model_property = settings.TELEGRAM_BOT[SETTINGS_HISTORY_LOOKUP_MODEL_PROPERTY]
        self.conv_classes = settings.TELEGRAM_BOT[SETTINGS_CONVERSATIONS]

    def get_conversation_handler(self, conv_class):
        try:
            class_def = import_string(conv_class)

            return class_def(
                logger=logging.getLogger(LOGGER_NAME),
                model_datetime_property=self.model_property,
                suffix=self.suffix,
            ).get_conversation_handler()
        except ImportError:
            return None

    @staticmethod
    def error_callback(update, context):
        update.message.reply_text(
            f'*ERR*: ``` {context.error} ```',
            parse_mode='markdown',
            reply_markup=ReplyKeyboardRemove(selective=True),
            reply_to_message_id=update.message.message_id,
            api_kwargs={'chat_id': update.message.chat.id},
        )

    def handle(self, *args, **options):
        updater = Updater(self.token)
        logger = logging.getLogger(LOGGER_NAME)
        for conversation in self.conv_classes:
            logger.info(f'Setting up conversation handler {conversation} ..')
            handler = self.get_conversation_handler(conversation)
            if handler:
                updater.dispatcher.add_handler(handler)
                logger.info(f'    > {conversation}: registered')
            else:
                logger.error(f'    > {conversation}: not registered')
        updater.dispatcher.add_error_handler(self.error_callback)
        logger.info('Setting up error handler ..')
        updater.start_polling()
        logger.info('Connect Reports Bot started!')
        updater.idle()
        logger.info('Connect Reports Bot stopped!')
