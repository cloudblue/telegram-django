import django

import pytest

from telegram import Bot
from telegram.utils.request import Request

from django.conf import settings

from connect.telegram_bot.telegram_conversation import TelegramConversation

settings.configure()
settings.DATABASES = {
    'default': {
        'ENGINE': 'django_fake_database_backends.backends.postgresql',
    },
}
django.setup()

from django_fake_model import models as f


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
    COMMANDS_DIR = None

    def __init__(self, logger, suffix=None):
        super().__init__(logger, suffix=suffix)
        self.name = 'test'
        self.model = None


class ConvTestFiltersCommands(TelegramConversation):
    COMMANDS_DIR = '/some/dir'

    def __init__(self, logger, suffix=None):
        super().__init__(logger, suffix=suffix)
        self.name = 'test'
        self.model = None

    @property
    def saved_filters(self):
        return [
            'avg_execution_24h',
        ]
