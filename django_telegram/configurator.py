import warnings

from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from django_telegram.bot.constants import (
    SETTINGS_CHAT_ID, SETTINGS_COMMANDS_SUFFIX,
    SETTINGS_CONVERSATIONS, SETTINGS_HISTORY_LOOKUP_MODEL_PROPERTY,
    SETTINGS_MW, SETTINGS_MW_CONDITIONS,
    SETTINGS_MW_CONDITIONS_FIELD, SETTINGS_MW_CONDITIONS_FIELD_VALUE,
    SETTINGS_MW_CONDITIONS_FUNC, SETTINGS_MW_CONDITIONS_TYPE,
    SETTINGS_MW_CONDITIONS_VALUE, SETTINGS_MW_MESSAGE,
    SETTINGS_MW_RULES, SETTINGS_MW_TRIGGER_CODES,
    SETTINGS_MW_VIEW, SETTINGS_TOKEN,
)


class TelegramBotConfigurator(object):

    def __init__(self, telegram_settings, django_mw_list):
        self.telegram_settings = telegram_settings
        self.django_mw_list = django_mw_list

    def _check_mw_config_rule_condition(self, condition):
        if SETTINGS_MW_CONDITIONS_TYPE not in condition.keys():
            raise ImproperlyConfigured(
                f'Condition "{SETTINGS_MW_CONDITIONS_TYPE}" key has not been set',
            )

        cond_type = condition[SETTINGS_MW_CONDITIONS_TYPE]
        cond_types = [SETTINGS_MW_CONDITIONS_FUNC, SETTINGS_MW_CONDITIONS_VALUE]
        if cond_type not in cond_types:
            raise ImproperlyConfigured(
                f'Condition "{SETTINGS_MW_CONDITIONS_TYPE}" key must be one of "{cond_types}"',
            )

        if cond_type == SETTINGS_MW_CONDITIONS_FUNC:
            try:
                import_string(condition[SETTINGS_MW_CONDITIONS_FUNC])
            except (KeyError, ImportError):
                raise ImproperlyConfigured(
                    f'Condition "{SETTINGS_MW_CONDITIONS_FUNC}" key must be set and have value. ',
                    'Or specified function could be found.',
                )

        if cond_type == SETTINGS_MW_CONDITIONS_VALUE:
            if SETTINGS_MW_CONDITIONS_FIELD not in condition.keys():
                raise ImproperlyConfigured(
                    f'Condition "{SETTINGS_MW_CONDITIONS_FIELD}" key must be set',
                )
            if not condition[SETTINGS_MW_CONDITIONS_FIELD]:
                raise ImproperlyConfigured(
                    f'Condition "{SETTINGS_MW_CONDITIONS_FIELD}" key is empty',
                )
            if SETTINGS_MW_CONDITIONS_FIELD_VALUE not in condition.keys():
                raise ImproperlyConfigured(
                    f'Condition "{SETTINGS_MW_CONDITIONS_FIELD_VALUE}" key must be set',
                )
            if not condition[SETTINGS_MW_CONDITIONS_FIELD_VALUE]:
                raise ImproperlyConfigured(
                    f'Condition "{SETTINGS_MW_CONDITIONS_FIELD_VALUE}" key is empty',
                )

    def _check_mw_rule(self, config):
        keys = config.keys()
        if SETTINGS_MW_VIEW not in keys or not config[SETTINGS_MW_VIEW]:
            raise ImproperlyConfigured(
                f'"{SETTINGS_MW_VIEW}" key has not been set',
            )

        if SETTINGS_MW_MESSAGE not in keys or not config[SETTINGS_MW_MESSAGE]:
            raise ImproperlyConfigured(
                f'"{SETTINGS_MW_MESSAGE}" key has not been set',
            )

        if SETTINGS_MW_TRIGGER_CODES not in keys or not config[SETTINGS_MW_TRIGGER_CODES]:
            raise ImproperlyConfigured(
                f'"{SETTINGS_MW_TRIGGER_CODES}" key has not been set',
            )

        if not isinstance(config[SETTINGS_MW_TRIGGER_CODES], list):
            raise ImproperlyConfigured(
                f'"{SETTINGS_MW_TRIGGER_CODES}" object must be a list.',
            )

        if any(filter(lambda x: not isinstance(x, int), config[SETTINGS_MW_TRIGGER_CODES])):
            raise ImproperlyConfigured(
                f'"{SETTINGS_MW_TRIGGER_CODES}" contains non-integer values',
            )

        if SETTINGS_MW_CONDITIONS in keys:
            self._check_mw_config_rule_condition(config[SETTINGS_MW_CONDITIONS])

    def _check_mw_settings(self):
        mw_fqdn = 'django_telegram.bot.middleware.TelegramMiddleware'
        if mw_fqdn not in self.django_mw_list:
            return

        settings_keys = self.telegram_settings.keys()
        if SETTINGS_MW not in settings_keys:
            raise ImproperlyConfigured(
                f'"{mw_fqdn}" is enabled, however "{SETTINGS_MW}" key has not been set.',
            )

        if not self.telegram_settings[SETTINGS_MW]:
            raise ImproperlyConfigured(
                f'"{mw_fqdn}" is enabled, however "{SETTINGS_MW}" is empty.',
            )

        if SETTINGS_CHAT_ID not in self.telegram_settings[SETTINGS_MW].keys():
            raise ImproperlyConfigured(f'"{SETTINGS_MW}[{SETTINGS_CHAT_ID}]" key has not been set.')

        if not self.telegram_settings[SETTINGS_MW][SETTINGS_CHAT_ID]:
            raise ImproperlyConfigured(f'"{SETTINGS_MW}[{SETTINGS_CHAT_ID}]" key has no value set.')

        if SETTINGS_MW_RULES not in self.telegram_settings[SETTINGS_MW].keys():
            raise ImproperlyConfigured(
                f'"{SETTINGS_MW}[{SETTINGS_MW_RULES}]" key has not been set.',
            )

        if not isinstance(self.telegram_settings[SETTINGS_MW][SETTINGS_MW_RULES], list):
            raise ImproperlyConfigured(
                f'"{SETTINGS_MW}[{SETTINGS_MW_RULES}]" object must be a list.',
            )

        for setting in self.telegram_settings[SETTINGS_MW][SETTINGS_MW_RULES]:
            index = self.telegram_settings[SETTINGS_MW][SETTINGS_MW_RULES].index(setting)
            try:
                self._check_mw_rule(setting)
            except ImproperlyConfigured as err:
                raise ImproperlyConfigured(
                    f'"{SETTINGS_MW}[{SETTINGS_MW_RULES}]" position "{index}" error: {str(err)}',
                )

    def run_check(self):
        settings_keys = self.telegram_settings.keys()
        if SETTINGS_TOKEN not in settings_keys:
            raise ImproperlyConfigured(
                f'"{SETTINGS_TOKEN}" key has not been set.',
            )
        if not self.telegram_settings[SETTINGS_TOKEN]:
            raise ImproperlyConfigured(
                f'"{SETTINGS_TOKEN}" key has no value set.',
            )
        if SETTINGS_COMMANDS_SUFFIX not in settings_keys:
            raise ImproperlyConfigured(
                f'"{SETTINGS_COMMANDS_SUFFIX}" key has not been set.',
            )
        if SETTINGS_HISTORY_LOOKUP_MODEL_PROPERTY not in settings_keys:
            raise ImproperlyConfigured(
                f'"{SETTINGS_HISTORY_LOOKUP_MODEL_PROPERTY}" key has not been set.',
            )
        if not self.telegram_settings[SETTINGS_HISTORY_LOOKUP_MODEL_PROPERTY]:
            raise ImproperlyConfigured(
                f'"{SETTINGS_HISTORY_LOOKUP_MODEL_PROPERTY}" key has no value set.',
            )
        if SETTINGS_CONVERSATIONS not in settings_keys:
            raise ImproperlyConfigured(
                f'"{SETTINGS_CONVERSATIONS}" key has not been set.',
            )
        if not isinstance(self.telegram_settings[SETTINGS_CONVERSATIONS], list):
            raise ImproperlyConfigured(
                f'"{SETTINGS_CONVERSATIONS}" must be a list of strings.',
            )

        if len(self.telegram_settings[SETTINGS_CONVERSATIONS]) == 0:
            warnings.warn(
                'Conversations list is empty, nothing will be setup for Telegram',
            )

        # middleware settings
        self._check_mw_settings()
