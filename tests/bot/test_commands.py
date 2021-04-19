from django_telegram.bot.commands import send_message


def test_send_message_not_successful():
    assert send_message('x') is False


def test_send_message_ok(mocker):
    mocker.patch('telegram.Bot._validate_token', return_value=True)
    mocker.patch('telegram.Bot._message', return_value=True)
    assert send_message('message') is True
