from connect.telegram_bot.bot import BotRunner

from tests.telegram_bot.conftest import ConvTest


def test_get_conversation_handler(mocker):
    mocker.patch('telegram.Bot._validate_token', return_value=True)
    mocker.patch('os.listdir', return_value=["x.py"])

    suffix = 'suffix'
    runner = BotRunner('token', suffix, '')
    runner.get_conversation = mocker.MagicMock(return_value=ConvTest)
    ch = runner.get_conversation_handler('command')

    assert ch is not None
    assert ch.entry_points[0].command == [f'convtest_{suffix}']


def test_get_conversation_handler_not_found(mocker):
    mocker.patch('telegram.Bot._validate_token', return_value=True)
    runner = BotRunner('token', 'suffix', '')
    runner.get_conversation = mocker.MagicMock(return_value=None)
    ch = runner.get_conversation_handler('command')

    assert ch is None


def test_setup_bot(mocker):
    mocker.patch('telegram.Bot._validate_token', return_value=True)
    mocker.patch('os.listdir', return_value=["x.py"])
    runner = BotRunner('token', 'suffix', '')
    runner.COMMANDS = ['reports']
    runner.get_conversation = mocker.MagicMock(return_value=ConvTest)
    ch = runner.setup_bot()

    assert ch is not None
    assert len(ch.dispatcher.handlers) == 1
    assert len(ch.dispatcher.error_handlers) == 1
