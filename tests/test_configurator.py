import pytest
from django.core.exceptions import ImproperlyConfigured

from django_telegram.configurator import TelegramBotConfigurator

MW_DEF = 'django_telegram.bot.middleware.TelegramMiddleware'


def cond_fn(data):
    return True


def test_condition_config_value_ok():
    c = TelegramBotConfigurator({}, [])
    condition = {
        'type': 'value',
        'field': 'f1',
        'field_value': 'f1_value',
    }

    assert c._check_mw_config_rule_condition(condition) is None


def test_condition_config_function_ok():
    c = TelegramBotConfigurator({}, [])
    condition = {
        'type': 'function',
        'function': 'tests.test_configurator.cond_fn',
    }

    assert c._check_mw_config_rule_condition(condition) is None


def test_condition_config_function_no_function():
    c = TelegramBotConfigurator({}, [])
    condition = {
        'type': 'function',
    }

    with pytest.raises(ImproperlyConfigured) as err:
        c._check_mw_config_rule_condition(condition)

    assert str((
        'Condition "function" key must be set and have value. ',
        'Or specified function could be found.',
    )) == str(err.value)


def test_condition_config_function_empty_function():
    c = TelegramBotConfigurator({}, [])
    condition = {
        'type': 'function',
        'function': '',
    }

    with pytest.raises(ImproperlyConfigured) as err:
        c._check_mw_config_rule_condition(condition)

    assert str((
        'Condition "function" key must be set and have value. ',
        'Or specified function could be found.',
    )) == str(err.value)


def test_condition_config_function_unknown_function():
    c = TelegramBotConfigurator({}, [])
    condition = {
        'type': 'function',
        'function': 'unknown',
    }

    with pytest.raises(ImproperlyConfigured) as err:
        c._check_mw_config_rule_condition(condition)

    assert str((
        'Condition "function" key must be set and have value. ',
        'Or specified function could be found.',
    )) == str(err.value)


def test_condition_config_no_type():
    c = TelegramBotConfigurator({}, [])
    condition = {
        'field': 'f1',
        'field_value': 'f1_value',
    }

    with pytest.raises(ImproperlyConfigured) as err:
        c._check_mw_config_rule_condition(condition)

    assert 'Condition "type" key has not been set' == str(err.value)


def test_condition_config_type_empty():
    c = TelegramBotConfigurator({}, [])
    condition = {
        'type': '',
        'field': 'f1',
        'field_value': 'f1_value',
    }

    with pytest.raises(ImproperlyConfigured) as err:
        c._check_mw_config_rule_condition(condition)

    assert 'Condition "type" key must be one of "[\'function\', \'value\']"' == str(err.value)


def test_condition_config_type_value_no_field():
    c = TelegramBotConfigurator({}, [])
    condition = {
        'type': 'value',
        'field_value': 'f1_value',
    }

    with pytest.raises(ImproperlyConfigured) as err:
        c._check_mw_config_rule_condition(condition)

    assert 'Condition "field" key must be set' == str(err.value)


def test_condition_config_type_value_field_empty():
    c = TelegramBotConfigurator({}, [])
    condition = {
        'type': 'value',
        'field': '',
        'field_value': 'f1_value',
    }

    with pytest.raises(ImproperlyConfigured) as err:
        c._check_mw_config_rule_condition(condition)

    assert 'Condition "field" key is empty' == str(err.value)


def test_condition_config_type_value_no_field_value():
    c = TelegramBotConfigurator({}, [])
    condition = {
        'type': 'value',
        'field': 'f',
    }

    with pytest.raises(ImproperlyConfigured) as err:
        c._check_mw_config_rule_condition(condition)

    assert 'Condition "field_value" key must be set' == str(err.value)


def test_condition_config_type_value_field_value_empty():
    c = TelegramBotConfigurator({}, [])
    condition = {
        'type': 'value',
        'field': 'f',
        'field_value': '',
    }

    with pytest.raises(ImproperlyConfigured) as err:
        c._check_mw_config_rule_condition(condition)

    assert 'Condition "field_value" key is empty' == str(err.value)


def test_mw_config_not_enabled():
    mw_config = {
        'TOKEN': 'token',
        'CHAT_ID': -1001339325227,
        'CONFIG': [{
            'view': 'reports-fail',
            'trigger_codes': [204],
            'conditions': {
                'type': 'value',
                'field': 'template.status',
                'field_value': 'blocked',
            },
            'message': 'Template is blocked due to report failed',
        }],
    }

    c = TelegramBotConfigurator(mw_config, [])

    assert c._check_mw_settings() is None


def test_mw_config_ok():
    mw_config = {
        'TOKEN': 'token',
        'MIDDLEWARE': {
            'CHAT_ID': -1001339325227,
            'RULES': [{
                'view': 'reports-fail',
                'trigger_codes': [204],
                'conditions': {
                    'type': 'value',
                    'field': 'template.status',
                    'field_value': 'blocked',
                },
                'message': 'Template is blocked due to report failed',
            }],
        },
    }

    c = TelegramBotConfigurator(mw_config, [MW_DEF])

    assert c._check_mw_settings() is None


def test_mw_config_no_chat_id():
    mw_config = {
        'TOKEN': 'token',
        'MIDDLEWARE': {
            'RULES': [{
                'view': 'reports-fail',
                'trigger_codes': [204],
                'conditions': {
                    'type': 'value',
                    'field': 'template.status',
                    'field_value': 'blocked',
                },
                'message': 'Template is blocked due to report failed',
            }],
        },
    }

    c = TelegramBotConfigurator(mw_config, [MW_DEF])

    with pytest.raises(ImproperlyConfigured) as err:
        c._check_mw_settings()

    assert '"MIDDLEWARE[CHAT_ID]" key has not been set.' == str(err.value)


def test_mw_config_chat_id_empty():
    mw_config = {
        'TOKEN': 'token',
        'MIDDLEWARE': {
            'CHAT_ID': '',
            'RULES': [{
                'view': 'reports-fail',
                'trigger_codes': [204],
                'conditions': {
                    'type': 'value',
                    'field': 'template.status',
                    'field_value': 'blocked',
                },
                'message': 'Template is blocked due to report failed',
            }],
        },
    }

    c = TelegramBotConfigurator(mw_config, [MW_DEF])

    with pytest.raises(ImproperlyConfigured) as err:
        c._check_mw_settings()

    assert '"MIDDLEWARE[CHAT_ID]" key has no value set.' == str(err.value)


def test_mw_config_no_rules():
    mw_config = {
        'TOKEN': 'token',
        'MIDDLEWARE': {
            'CHAT_ID': 123,
        },
    }

    c = TelegramBotConfigurator(mw_config, [MW_DEF])

    with pytest.raises(ImproperlyConfigured) as err:
        c._check_mw_settings()

    assert '"MIDDLEWARE[RULES]" key has not been set.' == str(err.value)


def test_mw_config_rules_not_list():
    mw_config = {
        'TOKEN': 'token',
        'MIDDLEWARE': {
            'CHAT_ID': 123,
            'RULES': {},
        },
    }

    c = TelegramBotConfigurator(mw_config, [MW_DEF])

    with pytest.raises(ImproperlyConfigured) as err:
        c._check_mw_settings()

    assert '"MIDDLEWARE[RULES]" object must be a list.' == str(err.value)


def test_mw_config_no_mw_key():
    mw_config = {
        'TOKEN': 'token',
    }

    c = TelegramBotConfigurator(mw_config, [MW_DEF])

    with pytest.raises(ImproperlyConfigured) as err:
        c._check_mw_settings()

    assert f'"{MW_DEF}" is enabled, however "MIDDLEWARE" key has not been set.' == str(err.value)


def test_mw_config_mw_empty():
    mw_config = {
        'TOKEN': 'token',
        'MIDDLEWARE': {},
    }

    c = TelegramBotConfigurator(mw_config, [MW_DEF])

    with pytest.raises(ImproperlyConfigured) as err:
        c._check_mw_settings()

    assert f'"{MW_DEF}" is enabled, however "MIDDLEWARE" is empty.' == str(
        err.value)


def test_mw_config_wrong_rule_condition():
    mw_config = {
        'TOKEN': 'token',
        'MIDDLEWARE': {
            'CHAT_ID': -1001339325227,
            'RULES': [{
                'view': 'reports-fail',
                'trigger_codes': [204],
                'conditions': {
                    'type': '',
                    'field': 'template.status',
                    'field_value': 'blocked',
                },
                'message': 'Template is blocked due to report failed',
            }],
        },
    }

    c = TelegramBotConfigurator(mw_config, [MW_DEF])

    with pytest.raises(ImproperlyConfigured) as err:
        c._check_mw_settings()

    err_expected = (
        '"MIDDLEWARE[RULES]" position "0" error: Condition "type"'
        ' key must be one of "[\'function\', \'value\']"'
    )

    assert err_expected == str(err.value)


def test_mw_config_wrong_rule_no_view():
    mw_config = {
        'TOKEN': 'token',
        'MIDDLEWARE': {
            'CHAT_ID': -1001339325227,
            'RULES': [{
                'trigger_codes': [204],
                'conditions': {
                    'type': 'value',
                    'field': 'template.status',
                    'field_value': 'blocked',
                },
                'message': 'Template is blocked due to report failed',
            }],
        },
    }

    c = TelegramBotConfigurator(mw_config, [MW_DEF])

    with pytest.raises(ImproperlyConfigured) as err:
        c._check_mw_settings()

    assert '"MIDDLEWARE[RULES]" position "0" error: "view" key has not been set' == str(err.value)


def test_mw_config_wrong_rule_view_empty():
    mw_config = {
        'TOKEN': 'token',
        'MIDDLEWARE': {
            'CHAT_ID': -1001339325227,
            'RULES': [{
                'view': '',
                'trigger_codes': [204],
                'conditions': {
                    'type': 'value',
                    'field': 'template.status',
                    'field_value': 'blocked',
                },
                'message': 'Template is blocked due to report failed',
            }],
        },
    }

    c = TelegramBotConfigurator(mw_config, [MW_DEF])

    with pytest.raises(ImproperlyConfigured) as err:
        c._check_mw_settings()

    assert '"MIDDLEWARE[RULES]" position "0" error: "view" key has not been set' == str(err.value)


def test_mw_config_wrong_rule_no_message():
    mw_config = {
        'TOKEN': 'token',
        'MIDDLEWARE': {
            'CHAT_ID': -1001339325227,
            'RULES': [{
                'view': 'view',
                'trigger_codes': [204],
                'conditions': {
                    'type': 'value',
                    'field': 'template.status',
                    'field_value': 'blocked',
                },
            }],
        },
    }

    c = TelegramBotConfigurator(mw_config, [MW_DEF])

    with pytest.raises(ImproperlyConfigured) as err:
        c._check_mw_settings()

    err_expected = '"MIDDLEWARE[RULES]" position "0" error: "message" key has not been set'

    assert err_expected == str(err.value)


def test_mw_config_wrong_rule_message_empty():
    mw_config = {
        'TOKEN': 'token',
        'MIDDLEWARE': {
            'CHAT_ID': -1001339325227,
            'RULES': [{
                'view': 'view',
                'trigger_codes': [204],
                'conditions': {
                    'type': 'value',
                    'field': 'template.status',
                    'field_value': 'blocked',
                },
                'message': '',
            }],
        },
    }

    c = TelegramBotConfigurator(mw_config, [MW_DEF])

    with pytest.raises(ImproperlyConfigured) as err:
        c._check_mw_settings()

    err_expected = '"MIDDLEWARE[RULES]" position "0" error: "message" key has not been set'

    assert err_expected == str(err.value)


def test_mw_config_wrong_rule_no_trigger_codes():
    mw_config = {
        'TOKEN': 'token',
        'MIDDLEWARE': {
            'CHAT_ID': -1001339325227,
            'RULES': [{
                'view': 'view',
                'conditions': {
                    'type': 'value',
                    'field': 'template.status',
                    'field_value': 'blocked',
                },
                'message': 'msg',
            }],
        },
    }

    c = TelegramBotConfigurator(mw_config, [MW_DEF])

    with pytest.raises(ImproperlyConfigured) as err:
        c._check_mw_settings()

    err_expected = '"MIDDLEWARE[RULES]" position "0" error: "trigger_codes" key has not been set'

    assert err_expected == str(err.value)


def test_mw_config_wrong_rule_trigger_codes_empty():
    mw_config = {
        'TOKEN': 'token',
        'MIDDLEWARE': {
            'CHAT_ID': -1001339325227,
            'RULES': [{
                'view': 'view',
                'trigger_codes': [],
                'conditions': {
                    'type': 'value',
                    'field': 'template.status',
                    'field_value': 'blocked',
                },
                'message': 'msg',
            }],
        },
    }

    c = TelegramBotConfigurator(mw_config, [MW_DEF])

    with pytest.raises(ImproperlyConfigured) as err:
        c._check_mw_settings()

    err_expected = '"MIDDLEWARE[RULES]" position "0" error: "trigger_codes" key has not been set'

    assert err_expected == str(err.value)


def test_mw_config_wrong_rule_trigger_codes_not_list():
    mw_config = {
        'TOKEN': 'token',
        'MIDDLEWARE': {
            'CHAT_ID': -1001339325227,
            'RULES': [{
                'view': 'view',
                'trigger_codes': {3: 4},
                'conditions': {
                    'type': 'value',
                    'field': 'template.status',
                    'field_value': 'blocked',
                },
                'message': 'msg',
            }],
        },
    }

    c = TelegramBotConfigurator(mw_config, [MW_DEF])

    with pytest.raises(ImproperlyConfigured) as err:
        c._check_mw_settings()

    err_expected = '"MIDDLEWARE[RULES]" position "0" error: "trigger_codes" object must be a list.'

    assert err_expected == str(err.value)


def test_mw_config_wrong_rule_trigger_codes_not_all_integers():
    mw_config = {
        'TOKEN': 'token',
        'MIDDLEWARE': {
            'CHAT_ID': -1001339325227,
            'RULES': [{
                'view': 'view',
                'trigger_codes': [1, 2, "3"],
                'conditions': {
                    'type': 'value',
                    'field': 'template.status',
                    'field_value': 'blocked',
                },
                'message': 'msg',
            }],
        },
    }

    c = TelegramBotConfigurator(mw_config, [MW_DEF])

    with pytest.raises(ImproperlyConfigured) as err:
        c._check_mw_settings()

    err_expected = (
        '"MIDDLEWARE[RULES]" position "0" error: '
        '"trigger_codes" contains non-integer values'
    )

    assert err_expected == str(err.value)


def test_mw_config_ok_rule_no_conditions():
    mw_config = {
        'TOKEN': 'token',
        'MIDDLEWARE': {
            'CHAT_ID': -1001339325227,
            'RULES': [{
                'view': 'view',
                'trigger_codes': [1, 2],
                'message': 'msg',
            }],
        },
    }

    c = TelegramBotConfigurator(mw_config, [MW_DEF])

    assert c._check_mw_settings() is None


def test_global_config_ok():
    mw_config = {
        'TOKEN': 'token',
        'COMMANDS_SUFFIX': 'local',
        'HISTORY_LOOKUP_MODEL_PROPERTY': 'prop',
        'CONVERSATIONS': [],
        'MIDDLEWARE': {
            'CHAT_ID': -1001339325227,
            'RULES': [{
                'view': 'view',
                'trigger_codes': [1, 2],
                'message': 'msg',
            }],
        },
    }

    c = TelegramBotConfigurator(mw_config, [MW_DEF])

    assert c.run_check() is None


def test_global_config_no_token():
    mw_config = {
        'COMMANDS_SUFFIX': 'local',
        'HISTORY_LOOKUP_MODEL_PROPERTY': 'prop',
        'CONVERSATIONS': [],
        'MIDDLEWARE': {
            'CHAT_ID': -1001339325227,
            'RULES': [{
                'view': 'view',
                'trigger_codes': [1, 2],
                'message': 'msg',
            }],
        },
    }

    c = TelegramBotConfigurator(mw_config, [MW_DEF])

    with pytest.raises(ImproperlyConfigured) as err:
        c.run_check()

    assert '"TOKEN" key has not been set.' == str(err.value)


def test_global_config_token_empty():
    mw_config = {
        'TOKEN': '',
        'COMMANDS_SUFFIX': 'local',
        'HISTORY_LOOKUP_MODEL_PROPERTY': 'prop',
        'CONVERSATIONS': [],
        'MIDDLEWARE': {
            'CHAT_ID': -1001339325227,
            'RULES': [{
                'view': 'view',
                'trigger_codes': [1, 2],
                'message': 'msg',
            }],
        },
    }

    c = TelegramBotConfigurator(mw_config, [MW_DEF])

    with pytest.raises(ImproperlyConfigured) as err:
        c.run_check()

    assert '"TOKEN" key has no value set.' == str(err.value)


def test_global_config_no_suffix():
    mw_config = {
        'TOKEN': 'token',
        'HISTORY_LOOKUP_MODEL_PROPERTY': 'prop',
        'CONVERSATIONS': [],
        'MIDDLEWARE': {
            'CHAT_ID': -1001339325227,
            'RULES': [{
                'view': 'view',
                'trigger_codes': [1, 2],
                'message': 'msg',
            }],
        },
    }

    c = TelegramBotConfigurator(mw_config, [MW_DEF])

    with pytest.raises(ImproperlyConfigured) as err:
        c.run_check()

    assert '"COMMANDS_SUFFIX" key has not been set.' == str(err.value)


def test_global_config_empty_suffix():
    mw_config = {
        'TOKEN': 'token',
        'COMMANDS_SUFFIX': '',
        'HISTORY_LOOKUP_MODEL_PROPERTY': 'prop',
        'CONVERSATIONS': [],
        'MIDDLEWARE': {
            'CHAT_ID': -1001339325227,
            'RULES': [{
                'view': 'view',
                'trigger_codes': [1, 2],
                'message': 'msg',
            }],
        },
    }

    c = TelegramBotConfigurator(mw_config, [MW_DEF])

    assert c.run_check() is None


def test_global_config_no_prop():
    mw_config = {
        'TOKEN': 'token',
        'COMMANDS_SUFFIX': '',
        'CONVERSATIONS': [],
        'MIDDLEWARE': {
            'CHAT_ID': -1001339325227,
            'RULES': [{
                'view': 'view',
                'trigger_codes': [1, 2],
                'message': 'msg',
            }],
        },
    }

    c = TelegramBotConfigurator(mw_config, [MW_DEF])

    with pytest.raises(ImproperlyConfigured) as err:
        c.run_check()

    assert '"HISTORY_LOOKUP_MODEL_PROPERTY" key has not been set.' == str(err.value)


def test_global_config_prop_empty():
    mw_config = {
        'TOKEN': 'token',
        'COMMANDS_SUFFIX': '',
        'HISTORY_LOOKUP_MODEL_PROPERTY': '',
        'CONVERSATIONS': [],
        'MIDDLEWARE': {
            'CHAT_ID': -1001339325227,
            'RULES': [{
                'view': 'view',
                'trigger_codes': [1, 2],
                'message': 'msg',
            }],
        },
    }

    c = TelegramBotConfigurator(mw_config, [MW_DEF])

    with pytest.raises(ImproperlyConfigured) as err:
        c.run_check()

    assert '"HISTORY_LOOKUP_MODEL_PROPERTY" key has no value set.' == str(err.value)


def test_global_config_no_conversations():
    mw_config = {
        'TOKEN': 'token',
        'COMMANDS_SUFFIX': '',
        'HISTORY_LOOKUP_MODEL_PROPERTY': 'prop',
        'MIDDLEWARE': {
            'CHAT_ID': -1001339325227,
            'RULES': [{
                'view': 'view',
                'trigger_codes': [1, 2],
                'message': 'msg',
            }],
        },
    }

    c = TelegramBotConfigurator(mw_config, [MW_DEF])

    with pytest.raises(ImproperlyConfigured) as err:
        c.run_check()

    assert '"CONVERSATIONS" key has not been set.' == str(err.value)


def test_global_config_conversations_not_list():
    mw_config = {
        'TOKEN': 'token',
        'COMMANDS_SUFFIX': '',
        'HISTORY_LOOKUP_MODEL_PROPERTY': 'prop',
        'CONVERSATIONS': {3: 4},
        'MIDDLEWARE': {
            'CHAT_ID': -1001339325227,
            'RULES': [{
                'view': 'view',
                'trigger_codes': [1, 2],
                'message': 'msg',
            }],
        },
    }

    c = TelegramBotConfigurator(mw_config, [MW_DEF])

    with pytest.raises(ImproperlyConfigured) as err:
        c.run_check()

    assert '"CONVERSATIONS" must be a list of strings.' == str(err.value)


def test_global_config_conversations_not_empty():
    mw_config = {
        'TOKEN': 'token',
        'COMMANDS_SUFFIX': '',
        'HISTORY_LOOKUP_MODEL_PROPERTY': 'prop',
        'CONVERSATIONS': ['test'],
        'MIDDLEWARE': {
            'CHAT_ID': -1001339325227,
            'RULES': [{
                'view': 'view',
                'trigger_codes': [1, 2],
                'message': 'msg',
            }],
        },
    }

    c = TelegramBotConfigurator(mw_config, [MW_DEF])

    assert c.run_check() is None
