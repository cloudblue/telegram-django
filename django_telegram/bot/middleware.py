import json

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.utils.module_loading import import_string

from django_telegram.bot.commands import send_message
from django_telegram.bot.constants import (
    SETTINGS_MW, SETTINGS_MW_CONDITIONS, SETTINGS_MW_CONDITIONS_FIELD,
    SETTINGS_MW_CONDITIONS_FIELD_VALUE, SETTINGS_MW_CONDITIONS_FUNC,
    SETTINGS_MW_CONDITIONS_TYPE, SETTINGS_MW_CONDITIONS_VALUE,
    SETTINGS_MW_MESSAGE, SETTINGS_MW_RULES,
    SETTINGS_MW_TRIGGER_CODES, SETTINGS_MW_VIEW,
)


class TelegramMiddleware(MiddlewareMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configs = settings.TELEGRAM_BOT[SETTINGS_MW]

    def get_field_value(self, model, field):
        field_parts = field.split('.')
        data = model
        for part in field_parts:
            data = data.get(part, None)
        return data

    def matches_config(self, current_config, response):
        if int(response.status_code) not in current_config[SETTINGS_MW_TRIGGER_CODES]:
            return False

        if SETTINGS_MW_CONDITIONS not in current_config.keys():
            return True

        conditions = current_config[SETTINGS_MW_CONDITIONS]
        cond_type = conditions[SETTINGS_MW_CONDITIONS_TYPE]
        if cond_type == SETTINGS_MW_CONDITIONS_VALUE:
            cond_field = conditions[SETTINGS_MW_CONDITIONS_FIELD]
            cond_value = conditions[SETTINGS_MW_CONDITIONS_FIELD_VALUE]
            field_value = self.get_field_value(json.loads(response.content), cond_field)
            if field_value == cond_value:
                return True

        if cond_type == SETTINGS_MW_CONDITIONS_FUNC:
            user_func = conditions[SETTINGS_MW_CONDITIONS_FUNC]
            user_func_def = import_string(user_func)
            try:
                return user_func_def(json.loads(response.content))
            except Exception:
                return False

    def process_response(self, request, response):
        if response.content_type.lower() != "application/json":
            return response

        view_name = request.resolver_match.view_name
        config_exists = any(
            filter(lambda x: x[SETTINGS_MW_VIEW] == view_name, self.configs[SETTINGS_MW_RULES]),
        )
        if config_exists:
            current_config = list(
                filter(lambda x: x[SETTINGS_MW_VIEW] == view_name, self.configs[SETTINGS_MW_RULES]),
            )[0]
            try:
                if self.matches_config(current_config, response):
                    send_message(
                        f'{request.resolver_match.view_name} with pk '
                        f'{request.resolver_match.kwargs.get("pk", None)} '
                        f'has ended with {response.status_code} '
                        f'and sends message: {current_config[SETTINGS_MW_MESSAGE]}',
                    )
            except Exception:
                #  we do not want this to affect any operations
                pass
        return response
