import logging
import os
import sys

import django

from telegram import ReplyKeyboardRemove
from telegram.ext import Updater

sys.path.append('/app')
logger = logging.getLogger('connect_reports_bot')


class BotRunner(object):
    def __init__(self, token, suffix, handlers_dir):
        self.token = token
        self.suffix = suffix
        self.handlers_dir = handlers_dir

    @staticmethod
    def setup_logging():
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s : %(message)s',
            level=logging.INFO,
        )

    def get_conversation(self, cmd_name):
        class_name = cmd_name.capitalize()
        full_path = f'{self.handlers_dir.rstrip("/").split("/")[-1]}.{cmd_name}'

        try:
            mod = __import__(full_path)
        except ImportError:
            return None
        return getattr(getattr(mod, cmd_name, None), class_name, None)

    def get_conversation_handler(self, cmd_name):
        class_def = self.get_conversation(cmd_name)
        if not class_def:
            return None
        return class_def(logger=logger, suffix=self.suffix).get_conversation_handler()

    @staticmethod
    def error_callback(update, context):
        update.message.reply_text(
            f'*ERR*: ``` {context.error} ```',
            parse_mode='markdown',
            reply_markup=ReplyKeyboardRemove(selective=True),
            reply_to_message_id=update.message.message_id,
            api_kwargs={'chat_id': update.message.chat.id},
        )

    def setup_bot(self):
        updater = Updater(self.token)
        commands = list(map(lambda x: x.split('.')[0], filter(
            lambda x: not x.startswith('__'),
            os.listdir(self.handlers_dir),
        )))

        for command in commands:
            handler = self.get_conversation_handler(command)
            if handler:
                updater.dispatcher.add_handler(handler)
        updater.dispatcher.add_error_handler(self.error_callback)
        return updater

    def run(self):
        self.setup_logging()
        django.setup()
        logger.info('Starting Connect Reports Bot...')
        bot = self.setup_bot()
        bot.start_polling()
        logger.info('Connect Reports Bot started!')
        bot.idle()
        logger.info('Connect Reports Bot stopped!')


if __name__ == '__main__':
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        exit('No token found. TELEGRAM_BOT_TOKEN env variable is empty.')
    django_settings = os.getenv('DJANGO_SETTINGS_MODULE')
    if not django_settings:
        exit('No django_settings found. DJANGO_SETTINGS_MODULE env variable is empty.')
    handlers_dir = os.getenv('TELEGRAM_BOT_HANDLERS')
    if not handlers_dir:
        exit('No conversation handlers found. TELEGRAM_BOT_HANDLERS env variable is empty.')
    commands_suffix = os.getenv('TELEGRAM_BOT_COMMAND_SUFFIX', '')
    runner = BotRunner(token, commands_suffix, handlers_dir)
    runner.run()
