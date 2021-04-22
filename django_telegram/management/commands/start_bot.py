from django.core.management.base import BaseCommand  # pragma: no cover

from django_telegram.bot.bot_runner import BotRunner  # pragma: no cover


class Command(BaseCommand):  # pragma: no cover
    help = "Start Django Telegram bot."

    def handle(self, *args, **options):
        bot_runner = BotRunner()
        bot_runner.handle()
