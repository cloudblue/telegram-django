import operator
import re
from io import StringIO
from abc import ABCMeta
from datetime import timedelta
from functools import reduce
from enum import Enum

import django
from django.db.models import Q, Sum
from django.utils import timezone
from django.core.management import call_command

from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, ConversationHandler, Filters, MessageHandler

from django_telegram.bot.constants import (
    BTN_CAPTION_BUILD_QUERY, BTN_CAPTION_CUSTOM_MGMT, BTN_CAPTION_USE_SAVED_FILTER,
    COUNT, DAYS, HOURS, NO, SUM, WEEKS, YES,
)
from django_telegram.bot.decorators.chat_context import chat_context
from django_telegram.bot.decorators.log_args import log_args
from django_telegram.bot.errors.saved_filter_not_found import SavedFilterNotFound
from django_telegram.bot.renderers.qs2md import render_as_list


class TelegramConversation(object, metaclass=ABCMeta):
    SUFFIX_REGEXP = r'^[\da-z_]{1,32}$'
    EMPTY_RESULT = 'Nothing found.'

    class STATUS(Enum):
        MODE_SELECTOR = 1
        BUILD = 2
        SAVED = 3
        SAVED_FILTER_SELECT = 11
        BUILD_PERIOD = 4
        BUILD_PERIOD_QUANTITY = 5
        BUILD_FILTERS_YES_NO = 6
        BUILD_FILTERS = 7
        BUILD_AGGREGATE_YES_NO = 8
        BUILD_AGGREGATE = 9
        BUILD_AGGREGATE_SUM_PROPERTY = 10
        CUSTOM_MGMT_COMMAND_SELECT = 12

    def __init__(self, logger, model_datetime_property, suffix=None):
        if suffix and not re.match(self.SUFFIX_REGEXP, suffix):
            raise ValueError(f'Suffix does not match {self.SUFFIX_REGEXP}')

        self.query_context = {}
        self.name = self.__class__.__name__.lower()
        self.logger = logger
        self.model = object
        self.suffix = suffix
        self.model_datetime_property = model_datetime_property
        self._default_query_context()
        self.chat_id = None
        if self.suffix:
            self.entrypoint = f'{self.__class__.__name__.lower()}_{self.suffix}'
            self.fallback = f'cancel_{self.suffix}'
        else:
            self.entrypoint = self.__class__.__name__.lower()
            self.fallback = 'cancel'

    def set_entrypoint_name(self, entrypoint_name):
        self.entrypoint = entrypoint_name

    def set_fallback_name(self, fallback_name):
        self.fallback = fallback_name

    def _default_query_context(self):
        self.query_context = {
            'mode': '',
            'period': {
                'uom': '',
                'quantity': 0,
                'timedelta': None,
            },
            'filters': [],
            'aggregate': {
                'type': '',
                'property': '',
            },
            'saved': '',
            'custom_command': '',
        }

    def _reply(self, update, data, keyboard=None):
        if keyboard:
            reply_keyboard = ReplyKeyboardMarkup(
                keyboard=keyboard,
                resize_keyboard=True,
                selective=True,
            )
        else:
            reply_keyboard = ReplyKeyboardRemove(selective=True)

        if type(data) in [django.db.models.query.QuerySet, list]:
            update.message.reply_text(
                render_as_list(data),
                parse_mode='markdown',
                reply_markup=reply_keyboard,
                reply_to_message_id=update.message.message_id,
                api_kwargs={'chat_id': self.chat_id},
            )
        else:
            update.message.reply_text(
                f'``` {data} ```',
                parse_mode='markdown',
                reply_markup=reply_keyboard,
                reply_to_message_id=update.message.message_id,
                api_kwargs={'chat_id': self.chat_id},
            )

    @property
    def saved_filter_regex(self):
        return f'^({"|".join(self.saved_filters)})$'

    @property
    def saved_filters(self):
        return []

    @property
    def custom_commands_regex(self):
        return f'^({"|".join(self.custom_commands)})$'

    @property
    def custom_commands(self):
        return []

    def set_saved_filter(self, s_filter):
        self.query_context['saved'] = s_filter

    @property
    def saved_filter(self):
        return self.query_context['saved']

    def set_custom_command(self, command):
        self.query_context['custom_command'] = command

    @property
    def custom_command(self):
        return self.query_context['custom_command']

    @property
    def saved_filter_selected(self):
        return self.saved_filter != ''

    @property
    def custom_command_selected(self):
        return self.custom_command != ''

    def set_aggregate_type(self, a_type):
        self.query_context['aggregate']['type'] = a_type

    def set_aggregate_property(self, a_property):
        self.query_context['aggregate']['property'] = a_property

    @property
    def aggregate_type(self):
        return self.query_context['aggregate']['type']

    @property
    def aggregate_property(self):
        return self.query_context['aggregate']['property']

    @property
    def has_aggregate(self):
        return self.query_context['aggregate']['type'] != ''

    def add_query_filter(self, key, value):
        self.query_context['filters'].append({key: value})

    @property
    def query_filters(self):
        return self.query_context['filters']

    def set_query_mode(self, mode):
        self.query_context['mode'] = mode

    @property
    def query_mode(self):
        return self.query_context['mode']

    def set_query_period_uom(self, uom):
        self.query_context['period']['uom'] = uom

    @property
    def query_period_uom(self):
        return self.query_context['period']['uom']

    @property
    def query_period_delta(self):
        return timedelta(**{self.query_period_uom: self.query_period_quantity})

    def set_query_period_quantity(self, quantity):
        self.query_context['period']['quantity'] = quantity

    @property
    def query_period_quantity(self):
        return int(self.query_context['period']['quantity'])

    @property
    def has_query_filters(self):
        return len(self.query_context['filters']) > 0

    def set_chat_id(self, user_id):
        self.chat_id = user_id

    def _end_conversation(self, update):
        self._reply(update, 'End of conversation')
        self.set_chat_id(None)
        return ConversationHandler.END

    def execute_custom_command(self, update, command):
        if command not in self.custom_commands:
            self._reply(update, 'Invalid command')
            return False

        out = StringIO()
        try:
            call_command(command, stderr=out, stdout=out)
            self._reply(update, f'Result {command}:\n{out.getvalue()}')
            return True
        except Exception as e:
            self._reply(update, f'Error {command}:\n{e}')
            return False

    @log_args
    def show_mode_select(self, update, context):
        self.set_chat_id(update.message.chat.id)
        self._default_query_context()
        reply_keyboard = [
            [KeyboardButton(text=BTN_CAPTION_BUILD_QUERY)],
            [KeyboardButton(text=BTN_CAPTION_USE_SAVED_FILTER)],
            [KeyboardButton(text=BTN_CAPTION_CUSTOM_MGMT)],
        ]
        self._reply(update, 'How do you want to proceed', reply_keyboard)
        return self.STATUS.MODE_SELECTOR

    def show_list_of_commands(self, update, context):
        self.set_chat_id(update.message.chat.id)
        classes = '\n - '.join([
            f'{cls.__name__.lower()}_{self.suffix}'
            for cls in TelegramConversation.__subclasses__()
        ])
        self._reply(update, f'Available commands:\n - {classes}')
        return ConversationHandler.END

    @log_args
    @chat_context
    def get_mode_show_mode_options(self, update, context):
        self.set_query_mode(update.message.text)
        if self.query_mode == BTN_CAPTION_BUILD_QUERY:
            reply_keyboard = [
                [
                    KeyboardButton(text=DAYS),
                    KeyboardButton(text=WEEKS),
                    KeyboardButton(text=HOURS),
                ],
            ]
            self._reply(update, 'Please select the period unit', reply_keyboard)
            return self.STATUS.BUILD_PERIOD

        if self.query_mode == BTN_CAPTION_USE_SAVED_FILTER:
            if not len(self.saved_filters):
                self._reply(update, 'No saved filters found for this command')
                return ConversationHandler.END
            else:
                reply_keyboard = [
                    [
                        KeyboardButton(text=i)
                        for i in self.saved_filters
                    ],
                ]
                self._reply(update, 'Please select saved filter', reply_keyboard)
                return self.STATUS.SAVED_FILTER_SELECT

        if self.query_mode == BTN_CAPTION_CUSTOM_MGMT:
            if not len(self.custom_commands):
                self._reply(update, 'No custom commands found for this command')
                return ConversationHandler.END
            else:
                reply_keyboard = [
                    [
                        KeyboardButton(text=i)
                        for i in self.custom_commands
                    ],
                ]
                self._reply(update, 'Please select command', reply_keyboard)
                return self.STATUS.CUSTOM_MGMT_COMMAND_SELECT

    @log_args
    @chat_context
    def get_custom_command_and_execute(self, update, context):
        self.set_custom_command(update.message.text)
        self.run_query(update)
        return self._end_conversation(update)

    @log_args
    @chat_context
    def get_period_uom_show_quantity(self, update, context):
        self.set_query_period_uom(update.message.text)
        self._reply(update, 'Please enter the period quantity')
        return self.STATUS.BUILD_PERIOD_QUANTITY

    @log_args
    @chat_context
    def get_quantity_show_yes_no_filters(self, update, context):
        self.set_query_period_quantity(update.message.text)
        reply_keyboard = [
            [KeyboardButton(text=YES)],
            [KeyboardButton(text=NO)],
        ]
        self._reply(update, 'Do you want to specify model filters?', reply_keyboard)
        return self.STATUS.BUILD_FILTERS_YES_NO

    @log_args
    @chat_context
    def get_yes_no_filters_and_proceed(self, update, context):
        if update.message.text == YES:
            self._reply(update, 'Provide model filters')
            return self.STATUS.BUILD_FILTERS
        else:
            reply_keyboard = [
                [KeyboardButton(text=YES)],
                [KeyboardButton(text=NO)],
            ]
            self._reply(update, 'Do you want to specify model aggregate?', reply_keyboard)
            return self.STATUS.BUILD_AGGREGATE_YES_NO

    @log_args
    @chat_context
    def get_yes_no_aggregate_and_proceed(self, update, context):
        if update.message.text == YES:
            reply_keyboard = [
                [
                    KeyboardButton(text=COUNT),
                    KeyboardButton(text=SUM),
                ],
            ]
            self._reply(update, 'Please select the aggregate', reply_keyboard)
            return self.STATUS.BUILD_AGGREGATE

        else:
            self.run_query(update)
            return self._end_conversation(update)

    @log_args
    @chat_context
    def get_filters_and_proceed(self, update, context):
        filters = update.message.text
        for model_filter in filters.split(','):
            field = model_filter.split('=')[0]
            field_value = model_filter.split('=')[1]
            self.add_query_filter(field, field_value)

        reply_keyboard = [
            [KeyboardButton(text=YES)],
            [KeyboardButton(text=NO)],
        ]
        self._reply(update, 'Do you want to specify model aggregate?', reply_keyboard)
        return self.STATUS.BUILD_AGGREGATE_YES_NO

    @log_args
    @chat_context
    def get_aggregate_property_and_proceed(self, update, context):
        self.set_aggregate_property(update.message.text)
        self.run_query(update)
        return self._end_conversation(update)

    @log_args
    @chat_context
    def get_saved_filter_and_proceed(self, update, context):
        self.set_saved_filter(update.message.text)
        self.run_query(update)
        return self._end_conversation(update)

    @log_args
    @chat_context
    def get_aggregate_and_proceed(self, update, context):
        self.set_aggregate_type(update.message.text)
        if self.aggregate_type == COUNT:
            self.run_query(update)
            return ConversationHandler.END

        if self.aggregate_type == SUM:
            self._reply(update, 'Provide property to aggregate')
            return self.STATUS.BUILD_AGGREGATE_SUM_PROPERTY

        return self._end_conversation(update)

    def _get_initial_queryset(self):
        return self.model.objects.all()

    def run_query(self, update):
        if self.saved_filter_selected:
            self.logger.info(f'Saved filter {self.model.__name__} : {self.saved_filter}')
            call_method = getattr(self, f'get_{self.saved_filter}', None)
            if not call_method:
                raise SavedFilterNotFound(f'{self.saved_filter} not found')
            call_method(update)
            return

        if self.custom_command_selected:
            self.logger.info(f'Custom command {self.model.__name__} : {self.custom_command}')
            self.execute_custom_command(update, command=self.custom_command)
            return

        self.logger.info(f'Lookup {self.query_context}')

        history_lookup = {
            f'{self.model_datetime_property}__gt': timezone.now() - self.query_period_delta,
        }
        queryset = self._get_initial_queryset().filter(**history_lookup)

        if self.has_query_filters:
            queryset = queryset.filter(
                reduce(operator.and_, (Q(**d) for d in self.query_filters)),
            )

        queryset = queryset.values('id', 'name', 'status')

        self.logger.info(f'Resulting queryset: {len(queryset)}')

        if self.has_aggregate:
            if self.aggregate_type == COUNT:
                self._reply(update, len(queryset))
                return

            if self.aggregate_type == SUM:
                queryset = queryset.aggregate(Sum(self.aggregate_property))
                self._reply(update, queryset[f'{self.aggregate_property}__sum'])
                return

        if queryset:
            self._reply(update, list(queryset))
        else:
            self._reply(update, self.EMPTY_RESULT)

    @log_args
    @chat_context
    def cancel(self, update, context):
        return self._end_conversation(update)

    def get_conversation_handler(self):
        modes = "|".join([
            BTN_CAPTION_BUILD_QUERY,
            BTN_CAPTION_USE_SAVED_FILTER,
            BTN_CAPTION_CUSTOM_MGMT,
        ])
        mode_sel_re = f'^({modes})$'

        return ConversationHandler(
            entry_points=[
                CommandHandler(self.entrypoint, self.show_mode_select),
                CommandHandler('commands', self.show_list_of_commands),
            ],
            states={
                self.STATUS.MODE_SELECTOR: [
                    MessageHandler(Filters.regex(mode_sel_re), self.get_mode_show_mode_options),
                ],
                self.STATUS.CUSTOM_MGMT_COMMAND_SELECT: [
                    MessageHandler(Filters.regex(
                        self.custom_commands_regex,
                    ), self.get_custom_command_and_execute),
                ],
                self.STATUS.BUILD_PERIOD: [
                    MessageHandler(Filters.regex(
                        f'^({DAYS}|{WEEKS}|{HOURS})$',
                    ), self.get_period_uom_show_quantity),
                ],
                self.STATUS.BUILD_PERIOD_QUANTITY: [
                    MessageHandler(
                        Filters.regex('^(\\d)+$'),
                        self.get_quantity_show_yes_no_filters,
                    ),
                ],
                self.STATUS.BUILD_FILTERS_YES_NO: [
                    MessageHandler(
                        Filters.regex(f'^({YES}|{NO})$'),
                        self.get_yes_no_filters_and_proceed,
                    ),
                ],
                self.STATUS.BUILD_AGGREGATE_YES_NO: [
                    MessageHandler(
                        Filters.regex(f'^({YES}|{NO})$'),
                        self.get_yes_no_aggregate_and_proceed,
                    ),
                ],
                self.STATUS.BUILD_FILTERS: [
                    MessageHandler(Filters.text, self.get_filters_and_proceed),
                ],
                self.STATUS.BUILD_AGGREGATE: [
                    MessageHandler(
                        Filters.regex(f'^({COUNT}|{SUM})$'),
                        self.get_aggregate_and_proceed,
                    ),
                ],
                self.STATUS.BUILD_AGGREGATE_SUM_PROPERTY: [
                    MessageHandler(Filters.text, self.get_aggregate_property_and_proceed),
                ],
                self.STATUS.SAVED_FILTER_SELECT: [
                    MessageHandler(
                        Filters.regex(self.saved_filter_regex),
                        self.get_saved_filter_and_proceed,
                    ),
                ],

            },
            fallbacks=[CommandHandler(self.fallback, self.cancel)],
        )
