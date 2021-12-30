import logging

from django.conf import settings
from rest_framework.response import Response

from django_telegram.bot.middleware import TelegramMiddleware

SEND_MSG_F = 'django_telegram.bot.middleware.send_message'


def cond_fn(data):
    raise Exception('ERR')


def test_process_response_not_json(mocker):
    mock_send_message = mocker.patch(
        SEND_MSG_F,
        return_value=True,
    )

    settings.TELEGRAM_BOT = {
        'CONVERSATIONS': [
            'tests.bot.conftest.ConvTest',
        ],
        'TOKEN': 'token',
        'COMMANDS_SUFFIX': 'dev',
        'HISTORY_LOOKUP_MODEL_PROPERTY': 'created_at',
        'MIDDLEWARE': {
            'CHAT_ID': 123,
            'RULES': [{
                'view': 'view',
                'trigger_codes': [1, 2],
                'conditions': {
                    'type': 'value',
                    'field': 'field',
                    'field_value': 'value',
                },
                'message': 'msg',
            }],
        },
    }

    response = Response(data="model", headers={'Content-Type': 'text/html'})

    def get_response(self):
        return response

    mw = TelegramMiddleware(get_response)

    assert mw(None) == response
    mock_send_message.assert_not_called()


def test_process_response_matches(django_request, mocker):
    mock_send_message = mocker.patch(
        SEND_MSG_F,
        return_value=True,
    )

    settings.TELEGRAM_BOT = {
        'CONVERSATIONS': [
            'tests.bot.conftest.ConvTest',
        ],
        'TOKEN': 'token',
        'COMMANDS_SUFFIX': 'dev',
        'HISTORY_LOOKUP_MODEL_PROPERTY': 'created_at',
        'MIDDLEWARE': {
            'CHAT_ID': 123,
            'RULES': [{
                'view': 'view',
                'trigger_codes': [1, 2],
                'conditions': {
                    'type': 'value',
                    'field': 'field',
                    'field_value': 'value',
                },
                'message': 'msg',
            }],
        },
    }
    response = Response(
        data={'field': 'value'},
        headers={'Content-Type': 'application/json'},
    )
    response._is_rendered = True
    response.content = '{"field":"value"}'
    response.render()
    response.status_code = 1

    def get_response(self):
        return response

    mw = TelegramMiddleware(get_response)

    assert mw(django_request) == response
    mock_send_message.assert_called_once_with(
        '[dev] view with pk pk-1 has ended with 1 and sends message: msg',
    )


def test_process_response_matches_no_conditions(django_request, mocker):
    mock_send_message = mocker.patch(
        SEND_MSG_F,
        return_value=True,
    )

    settings.TELEGRAM_BOT = {
        'CONVERSATIONS': [
            'tests.bot.conftest.ConvTest',
        ],
        'TOKEN': 'token',
        'COMMANDS_SUFFIX': 'dev',
        'HISTORY_LOOKUP_MODEL_PROPERTY': 'created_at',
        'MIDDLEWARE': {
            'CHAT_ID': 123,
            'RULES': [{
                'view': 'view',
                'trigger_codes': [1, 2],
                'message': 'msg',
            }],
        },
    }
    response = Response(
        data={'field': 'value'},
        headers={'Content-Type': 'application/json'},
    )
    response._is_rendered = True
    response.content = '{"field":"value"}'
    response.render()
    response.status_code = 1

    def get_response(self):
        return response

    mw = TelegramMiddleware(get_response)
    assert mw(django_request) == response
    mock_send_message.assert_called_once_with(
        '[dev] view with pk pk-1 has ended with 1 and sends message: msg',
    )


def test_process_response_matches_by_func(django_request, mocker):
    mock_send_message = mocker.patch(
        SEND_MSG_F,
        return_value=True,
    )

    settings.TELEGRAM_BOT = {
        'CONVERSATIONS': [
            'tests.bot.conftest.ConvTest',
        ],
        'TOKEN': 'token',
        'COMMANDS_SUFFIX': 'dev',
        'HISTORY_LOOKUP_MODEL_PROPERTY': 'created_at',
        'MIDDLEWARE': {
            'CHAT_ID': 123,
            'RULES': [{
                'view': 'view',
                'conditions': {
                    'type': 'function',
                    'function': 'tests.test_configurator.cond_fn',
                },
                'trigger_codes': [1, 2],
                'message': 'msg',
            }],
        },
    }
    response = Response(
        data={'field': 'value'},
        headers={'Content-Type': 'application/json'},
    )
    response._is_rendered = True
    response.content = '{"field":"value"}'
    response.render()
    response.status_code = 1

    def get_response(self):
        return response

    mw = TelegramMiddleware(get_response)

    assert mw(django_request) == response
    mock_send_message.assert_called_once_with(
        '[dev] view with pk pk-1 has ended with 1 and sends message: msg',
    )


def test_process_response_204_no_content(django_request, mocker):
    mock_send_message = mocker.patch(
        SEND_MSG_F,
        return_value=True,
    )

    settings.TELEGRAM_BOT = {
        'CONVERSATIONS': [
            'tests.bot.conftest.ConvTest',
        ],
        'TOKEN': 'token',
        'COMMANDS_SUFFIX': 'dev',
        'HISTORY_LOOKUP_MODEL_PROPERTY': 'created_at',
        'MIDDLEWARE': {
            'CHAT_ID': 123,
            'RULES': [{
                'view': 'view',
                'conditions': {
                    'type': 'function',
                    'function': 'tests.test_configurator.cond_fn',
                },
                'trigger_codes': [1, 2],
                'message': 'msg',
            }],
        },
    }
    response = Response(
        data={'field': 'value'},
        headers={'Content-Type': 'application/json'},
    )
    response._is_rendered = True
    response.content = '{"field":"value"}'
    response.render()
    response.status_code = 204

    def get_response(self):
        return response

    mw = TelegramMiddleware(get_response)

    assert mw(django_request) == response
    mock_send_message.assert_not_called()


def test_process_response_matches_by_func_err(django_request, mocker):
    mock_send_message = mocker.patch(
        SEND_MSG_F,
        return_value=True,
    )

    settings.TELEGRAM_BOT = {
        'CONVERSATIONS': [
            'tests.bot.conftest.ConvTest',
        ],
        'TOKEN': 'token',
        'COMMANDS_SUFFIX': 'dev',
        'HISTORY_LOOKUP_MODEL_PROPERTY': 'created_at',
        'MIDDLEWARE': {
            'CHAT_ID': 123,
            'RULES': [{
                'view': 'view',
                'conditions': {
                    'type': 'function',
                    'function': 'tests.bot.test_middleware.cond_fn',
                },
                'trigger_codes': [1, 2],
                'message': 'msg',
            }],
        },
    }
    response = Response(
        data={'field': 'value'},
        headers={'Content-Type': 'application/json'},
    )
    response._is_rendered = True
    response.content = '{"field":"value"}'
    response.render()
    response.status_code = 1

    def get_response(self):
        return response

    mw = TelegramMiddleware(get_response)
    assert mw(django_request) == response
    mock_send_message.assert_not_called()


def test_process_response_not_matches_by_response_code(django_request, mocker):
    mock_send_message = mocker.patch(
        SEND_MSG_F,
        return_value=True,
    )

    settings.TELEGRAM_BOT = {
        'CONVERSATIONS': [
            'tests.bot.conftest.ConvTest',
        ],
        'TOKEN': 'token',
        'COMMANDS_SUFFIX': 'dev',
        'HISTORY_LOOKUP_MODEL_PROPERTY': 'created_at',
        'MIDDLEWARE': {
            'CHAT_ID': 123,
            'RULES': [{
                'view': 'view',
                'trigger_codes': [1, 2],
                'conditions': {
                    'type': 'value',
                    'field': 'field',
                    'field_value': 'value',
                },
                'message': 'msg',
            }],
        },
    }
    response = Response(
        data={'field': 'value'},
        headers={'Content-Type': 'application/json'},
    )
    response._is_rendered = True
    response.content = '{"field":"value"}'
    response.render()
    response.status_code = 5

    def get_response(self):
        return response

    mw = TelegramMiddleware(get_response)

    assert mw(django_request) == response
    mock_send_message.assert_not_called()


def test_get_field_value():
    settings.TELEGRAM_BOT = {
        'CONVERSATIONS': [
            'tests.bot.conftest.ConvTest',
        ],
        'TOKEN': 'token',
        'COMMANDS_SUFFIX': 'dev',
        'HISTORY_LOOKUP_MODEL_PROPERTY': 'created_at',
        'MIDDLEWARE': {
            'CHAT_ID': 123,
            'RULES': [{
                'view': 'view',
                'trigger_codes': [1, 2],
                'conditions': {
                    'type': 'value',
                    'field': 'field',
                    'field_value': 'value',
                },
                'message': 'msg',
            }],
        },
    }

    mw = TelegramMiddleware(None)
    model = {
        'field': 'value',
    }

    assert mw.get_field_value(model, 'field') == 'value'


def test_get_field_value_complex():
    settings.TELEGRAM_BOT = {
        'CONVERSATIONS': [
            'tests.bot.conftest.ConvTest',
        ],
        'TOKEN': 'token',
        'COMMANDS_SUFFIX': 'dev',
        'HISTORY_LOOKUP_MODEL_PROPERTY': 'created_at',
        'MIDDLEWARE': {
            'CHAT_ID': 123,
            'RULES': [{
                'view': 'view',
                'trigger_codes': [1, 2],
                'conditions': {
                    'type': 'value',
                    'field': 'field.field.field',
                    'field_value': 'value',
                },
                'message': 'msg',
            }],
        },
    }

    mw = TelegramMiddleware(None)
    model = {
        'field': {
            'field': {
                'field': 'value',
            },
        },
    }

    assert mw.get_field_value(model, 'field.field.field') == 'value'


def test_process_response_config_does_not_exist(django_request, mocker):
    mock_send_message = mocker.patch(
        SEND_MSG_F,
        return_value=True,
    )

    settings.TELEGRAM_BOT = {
        'CONVERSATIONS': [
            'tests.bot.conftest.ConvTest',
        ],
        'TOKEN': 'token',
        'COMMANDS_SUFFIX': 'dev',
        'HISTORY_LOOKUP_MODEL_PROPERTY': 'created_at',
        'MIDDLEWARE': {
            'CHAT_ID': 123,
            'RULES': [{
                'view': 'view-2',
                'conditions': {
                    'type': 'function',
                    'function': 'tests.bot.test_middleware.cond_fn',
                },
                'trigger_codes': [1, 2],
                'message': 'msg',
            }],
        },
    }
    response = Response(
        data={'field': 'value'},
        headers={'Content-Type': 'application/json'},
    )
    response._is_rendered = True
    response.content = '{"field":"value"}'
    response.render()
    response.status_code = 1

    def get_response(self):
        return response

    mw = TelegramMiddleware(get_response)
    assert mw(django_request) == response
    mock_send_message.assert_not_called()


def test_process_response_exception(django_request, mocker, caplog):
    mock_send_message = mocker.patch(
        SEND_MSG_F,
        side_effect=Exception('ERR'),
    )

    settings.TELEGRAM_BOT = {
        'CONVERSATIONS': [
            'tests.bot.conftest.ConvTest',
        ],
        'TOKEN': 'token',
        'COMMANDS_SUFFIX': 'dev',
        'HISTORY_LOOKUP_MODEL_PROPERTY': 'created_at',
        'MIDDLEWARE': {
            'CHAT_ID': 123,
            'RULES': [{
                'view': 'view',
                'conditions': {
                    'type': 'function',
                    'function': 'tests.test_configurator.cond_fn',
                },
                'trigger_codes': [1, 2],
                'message': 'msg',
            }],
        },
    }
    response = Response(
        data={'field': 'value'},
        headers={'Content-Type': 'application/json'},
    )
    response._is_rendered = True
    response.content = '{"field":"value"}'
    response.render()
    response.status_code = 1

    def get_response(self):
        return response

    with caplog.at_level(logging.ERROR):
        mw = TelegramMiddleware(get_response)
    assert mw(django_request) == response
    mock_send_message.assert_called_once()
    expected_config = settings.TELEGRAM_BOT['MIDDLEWARE']['RULES'][0]
    assert (
        f'TelegramMiddleware rule {expected_config} finished with error: ERR'
    ) in caplog.records[0].message
