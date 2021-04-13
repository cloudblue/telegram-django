from django.core.management.base import BaseCommand

from django_telegram.bot.bot_runner import BotRunner


class Command(BaseCommand):  # pragma: no cover
    help = "Start Django Telegram bot."

    def handle(self, *args, **options):
        bot_runner = BotRunner()
        bot_runner.handle()
