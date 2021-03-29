# Connect Telegram Bot

![pyversions](https://img.shields.io/pypi/pyversions/connect-telegram-bot.svg) [![PyPi Status](https://img.shields.io/pypi/v/connect-telegram-bot.svg)](https://pypi.org/project/connect-telegram-bot/) [![Build Connect Telegram Bot](https://github.com/cloudblue/connect-telegram-bot/actions/workflows/build.yml/badge.svg)](https://github.com/cloudblue/connect-telegram-bot/actions/workflows/build.yml) [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=connect-telegram-bot&metric=alert_status)](https://sonarcloud.io/dashboard?id=connect-telegram-bot) [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=connect-telegram-bot&metric=coverage)](https://sonarcloud.io/dashboard?id=connect-telegram-bot) [![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=connect-telegram-bot&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=connect-telegram-bot)

## Introduction

`Connect Telegram Bot` is the base class which helps to build custom commands for the django models. It allows getting historical data from django models, as well as develop custom pre-defined filters and execute custom django management commands (i.e. those which are executed through  `python manage.py $command`)

## Install

`Connect Telegram Bot` requires python 3.8 or later and has the following dependencies:

* python-telegram-bot >=13.3
* django>=2.2.19

`Connect Telegram Bot` can be installed from [pypi.org](https://pypi.org/project/connect-telegram-bot/) using pip:

```
$ pip install connect-telegram-bot
```

## Running The Bot
### Define your command class extending the base

For example:

``` 

from myapp.models import MyAppModel

from telegram_bot.telegram_conversation import TelegramConversation


class MyAppConversation(TelegramConversation):
    COMMANDS_DIR = '/app/myapp/management/commands'

    def __init__(self, logger, suffix):
        super().__init__(logger, suffix)
        self.model = MyAppModel

    @property
    def saved_filters(self):
        return [
            'count',
        ]

    def get_count(self, update):
        amount = self._get_initial_queryset().count()
        self._reply(update, amount)
        self._default_query_context()


```

Create a directory in your project where these conversation implementations will be placed.
`Connect Telegram Bot` requires multiple environment variables to be setup before executing:

| Variable      | Description  |
| ------------- |:-------------|
|`TELEGRAM_BOT_TOKEN`|Telegram Token for the bot. Please refer to https://core.telegram.org/bots on how to create a bot.|
|`DJANGO_SETTINGS_MODULE`|Django settings package for current project.|
|`TELEGRAM_BOT_HANDLERS`|Directory where custom conversations (handlers) were placed, i.e. where we would put our `MyAppConversation` from above|
|`TELEGRAM_BOT_COMMAND_SUFFIX`|In case of having multiple instances of the bot (with the same commands) we want to add some suffix to the commands, so that only specific bot is getting the command, so command becomes `myappconversation_${SUFFIX}`. If there is no need to have multiple instances of the same bot in the chat -- just leave this undefined. |

### Running The Bot

`export TELEGRAM_BOT_TOKEN='....'; export DJANGO_SETTINGS_MODULE='settings.common'; export TELEGRAM_BOT_HANDLERS='/app/telegram_bot/conversation_handlers/'; export TELEGRAM_BOT_COMMAND_SUFFIX='suf1'; python telegram_bot/bot.py`

## Testing

* Create virtualenv
* Install project dependencies
```commandline
python -m pip install --upgrade pip
pip install poetry
poetry update
```
* Run tests
```commandline
poetry run pytest
```


## License

``Connect Telegram Bot`` is released under the [Apache License Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).