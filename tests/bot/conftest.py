import django

import pytest

from telegram import Bot
from telegram.utils.request import Request

from django.conf import settings

from django_telegram.bot.telegram_conversation import TelegramConversation

settings.configure()
settings.DATABASES = {
    'default': {
        'ENGINE': 'django_fake_database_backends.backends.postgresql',
    },
}
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
django.setup()

from django_fake_model import models as f


@pytest.fixture(scope='function')
def django_request():
    class MockRequest(object):
        pass

    class MockResolver(object):
        pass

    r = MockRequest()
    r.resolver_match = MockResolver()
    r.resolver_match.view_name = 'view'
    r.resolver_match.kwargs = {'pk': 'pk-1'}

    return r


@pytest.fixture(scope='function')
def telegram_bot(mocker):
    mocker.patch('telegram.Bot._validate_token', return_value=True)

    return Bot('12', request=Request(10))


class FakeModel(f.FakeModel):
    name = f.models.CharField(max_length=100)
    id = f.models.CharField(max_length=100)
    status = f.models.CharField(max_length=100)
    aggr_property = f.models.IntegerField(default=1)
    created_at = f.models.DateTimeField(
        'Created',
        auto_now_add=True,
        db_index=True,
    )


class ConvTest(TelegramConversation):
    def __init__(self, logger, model_datetime_property, suffix=None):
        super().__init__(logger, model_datetime_property, suffix=suffix)
        self.name = 'test'
        self.model = None


class ConvTestFiltersCommands(TelegramConversation):
    def __init__(self, logger, model_datetime_property, suffix=None):
        super().__init__(logger, model_datetime_property, suffix=suffix)
        self.name = 'test'
        self.model = None

    @property
    def saved_filters(self):
        return [
            'avg_execution_24h',
        ]

    @property
    def custom_commands(self):
        return ['xx']
