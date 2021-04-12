from django_telegram.bot.bot_runner import BotRunner

from django.conf import settings


def test_get_conversation_handler():
    runner = BotRunner()
    ch = runner.get_conversation_handler(settings.TELEGRAM_BOT["CONVERSATIONS"][0])

    assert ch is not None
    assert ch.entry_points[0].command == [f'convtest_{settings.TELEGRAM_BOT["COMMANDS_SUFFIX"]}']


def test_get_conversation_handler_not_found():
    runner = BotRunner()
    ch = runner.get_conversation_handler('tests.bot.conftest.ConvTest2')

    assert ch is None
