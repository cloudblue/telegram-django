# Django Telegram Bot

![pyversions](https://img.shields.io/pypi/pyversions/telegram-django.svg) [![PyPi Status](https://img.shields.io/pypi/v/telegram-django.svg)](https://pypi.org/project/telegram-django/) [![Build Django Telegram Bot](https://github.com/cloudblue/telegram-django/actions/workflows/build.yml/badge.svg)](https://github.com/cloudblue/telegram-django/actions/workflows/build.yml) [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=telegram-django&metric=alert_status)](https://sonarcloud.io/dashboard?id=telegram-django) [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=telegram-django&metric=coverage)](https://sonarcloud.io/dashboard?id=telegram-django) [![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=telegram-django&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=telegram-django)

## Introduction

`Django Telegram Bot` is the base class which helps to build custom commands for the django models. It allows getting historical data from django models, as well as develop custom pre-defined filters and execute custom django management commands (i.e. those which are executed through  `python manage.py $command`)

## Install

`Django Telegram Bot` requires python 3.8 or later and has the following dependencies:

* python-telegram-bot >=13.3
* django>=2.2.20

`Django Telegram Bot` can be installed from [pypi.org](https://pypi.org/project/telegram-django/) using pip:

```
$ pip install telegram-django
```

## Running The Bot
### Define your command class extending the base

For example:

``` 

from myapp.models import MyAppModel

from telegram_bot.telegram_conversation import TelegramConversation


class MyAppConversation(TelegramConversation):
    def __init__(self, logger, model_datetime_property, suffix):
        super().__init__(logger, model_datetime_property, suffix)
        self.model = MyAppModel

    @property
    def custom_commands(self):
        return [
            'custom_command1',
        ]
        
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

The method ```custom_commands``` must return a list of defined django commands which can be executed by this conversation handler. These commands are standard django commands which are normally executed via ```python manage.py $command```.
The method ```saved_filters``` must return a list of defined custom filters. The filter's body must be implemented in the same class using the convention ```get_$filter_name```, like in the example above: for ```count``` filter the ```get_count``` method is implemented.

Add the following sections to your ```settings.py```:

Define application in ```INSTALLED_APPS```
```
    INSTALLED_APPS = [
        ...
        'django_telegram',
        ...
    ]
```
Add section ```TELEGRAM_BOT``` for bot configuration
```
TELEGRAM_BOT = {
    'CONVERSATIONS': [
        'myapp.package1.package2.MyAppConversation',
    ],
    'TOKEN': '',
    'COMMANDS_SUFFIX': None,
    'HISTORY_LOOKUP_MODEL_PROPERTY': ''
}
```
Add section ```django_telegram_bot``` to logger configuration
```
LOGGING = {
...
    'loggers': {
...
        'django_telegram_bot': {
            'handlers': ['console'],
            'level': 'INFO',
        },
...
    },
...
}
```

Settings description:

| Variable      | Description  |
| ------------- |:-------------|
|`TOKEN`|Telegram Token for the bot. Please refer to https://core.telegram.org/bots on how to create a bot.|
|`CONVERSATIONS`|List of FQDNs for classes which implement and provide conversation instances|
|`HISTORY_LOOKUP_MODEL_PROPERTY`|Property of the django model of DateTime type which is used to do history lookups|
|`COMMANDS_SUFFIX`|In case of having multiple instances of the bot (with the same commands) we want to add some suffix to the commands, so that only specific bot is getting the command, so command becomes `myappconversation_${SUFFIX}`. If there is no need to have multiple instances of the same bot in the chat -- just leave this as ```None```. |

### Running The Bot

`python manage.py start_bot`

## Middleware
The library also provides a way to analyse **responses of type application/json** and based on defined rules send pre-defined messages.
To enable middleware add the following line into your ```settings.MIDDLEWARE```
```
MIDDLEWARE = [
...
    'django_telegram.bot.middleware.TelegramMiddleware',
]
```

Extend previously defined configuration in ```settings.py``` with the following
```
TELEGRAM_BOT = {
    'CONVERSATIONS': [
        'myapp.package1.package2.MyAppConversation',
    ],
    'TOKEN': '',
    'COMMANDS_SUFFIX': None,
    'HISTORY_LOOKUP_MODEL_PROPERTY': '',
    'MIDDLEWARE': {
        'CHAT_ID': -12356789,
        'RULES': [{
            'view': 'view',
            'trigger_codes': [204, 200],
            'conditions': {
                'type': 'value',
                'field': 'field',
                'field_value': 'value',
            },
            'message': 'Message when this condition happened!',
        }],
    }
}
```
Settings description:

| Variable      | Description  |
| ------------- |:-------------|
|`CHAT_ID`|Telegram chat id to where the bot must send messages. Typically an integer like ```-12345677898```|
|`RULES`|List of rules objects which configure a case when message must be sent|
|`RULES[i].view`|View id in resolver definition, i.e. ```/v1/reports/fail/123``` URI would be a ```reports-fail```|
|`RULES[i].trigger_codes`|List of HTTP codes in response where this rule needs to be triggered|
|`RULES[i].conditions`|Optional. Additional checks which need to be done before sending the message|
|`RULES[i].conditions.type`|Type of condition, can be either 'function' (when validation is done by user defined function) or 'value' (when validation is done by simple field/value comparison of response JSON).|
|`RULES[i].conditions.function`|Required if `RULES[i].conditions.type` is `function` otherwise ignored. User defined function which receives as input response JSON as dict and must return either `True` or `False`|
|`RULES[i].conditions.field`|Required if `RULES[i].conditions.type` is `value` otherwise ignored. Field to look up in response JSON|
|`RULES[i].conditions.field_value`|Required if `RULES[i].conditions.type` is `value` otherwise ignored. Expected value to look up in response JSON|
|`RULES[i].message`|Message which needs to be sent to Telegram in case all conditions match|


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

``Django Telegram Bot`` is released under the [Apache License Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).