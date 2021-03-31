import logging

import pytest

from django.utils import timezone

from telegram import Chat, Message
from telegram.ext import ConversationHandler, Updater

from connect.telegram_bot.constants import (
    BTN_CAPTION_BUILD_QUERY, BTN_CAPTION_CUSTOM_MGMT, BTN_CAPTION_USE_SAVED_FILTER,
    COUNT, NO, SUM, WEEKS, YES,
)
from connect.telegram_bot.telegram_conversation import TelegramConversation
from connect.telegram_bot.errors.saved_filter_not_found import SavedFilterNotFound

from tests.telegram_bot import INITIAL_QUERY_SET_METHOD, TELEGRAM_REPLY_METHOD
from tests.telegram_bot.conftest import ConvTest, ConvTestFiltersCommands, FakeModel

from django_mock_queries.query import MockModel, MockSet


def test_conversation_handler():
    log = logging.getLogger()
    c = ConvTest(log, suffix='dev')

    handler = c.get_conversation_handler()
    entry_point = handler.entry_points[0]
    fallback = handler.fallbacks[0]

    assert len(handler.states) == 10
    assert entry_point.command == [f'{c.__class__.__name__.lower()}_dev']
    assert fallback.command == ['cancel_dev']


def test_conversation_handler_no_suffix():
    log = logging.getLogger()
    c = ConvTest(log)

    handler = c.get_conversation_handler()
    entry_point = handler.entry_points[0]
    fallback = handler.fallbacks[0]

    assert len(handler.states) == 10
    assert entry_point.command == [c.__class__.__name__.lower()]
    assert fallback.command == ['cancel']


def test_conversation_handler_custom_fb_and_entry():
    log = logging.getLogger()
    c = ConvTest(log, suffix='dev')
    c.set_entrypoint_name('test_start')
    c.set_fallback_name('test_end')

    handler = c.get_conversation_handler()
    entry_point = handler.entry_points[0]
    fallback = handler.fallbacks[0]

    assert len(handler.states) == 10
    assert entry_point.command == ['test_start']
    assert fallback.command == ['test_end']


def test_cancel(mocker, telegram_bot):
    log = logging.getLogger()
    c = ConvTest(log, suffix='dev')
    c.set_chat_id(1)

    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    updater = Updater(bot=telegram_bot)
    message = Message(1, timezone.now(), chat=None)
    chat = Chat(1, 'user')
    message.chat = chat
    updater.message = message
    data = c.cancel(updater, None)

    assert mock.called
    assert mock.call_args[0] == ('``` End of conversation ```',)
    assert data == ConversationHandler.END


def test_show_mode_select(mocker, telegram_bot):
    log = logging.getLogger()
    c = ConvTest(log, suffix='dev')
    c.set_chat_id(1)

    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    updater = Updater(bot=telegram_bot)
    message = Message(1, timezone.now(), chat=None)
    chat = Chat(1, 'user')
    message.chat = chat
    updater.message = message
    data = c.show_mode_select(updater, None)

    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == TelegramConversation.STATUS.MODE_SELECTOR


def test_get_mode_show_mode_options(mocker, telegram_bot):
    log = logging.getLogger()
    c = ConvTest(log, suffix='dev')
    c.set_chat_id(1)

    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    updater = Updater(bot=telegram_bot)
    message = Message(1, timezone.now(), chat=None, text=BTN_CAPTION_BUILD_QUERY)
    chat = Chat(1, 'user')
    message.chat = chat
    updater.message = message
    data = c.get_mode_show_mode_options(updater, None)

    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == TelegramConversation.STATUS.BUILD_PERIOD

    message = Message(1, timezone.now(), chat=None, text=BTN_CAPTION_USE_SAVED_FILTER)
    chat = Chat(1, 'user')
    message.chat = chat
    updater.message = message
    data = c.get_mode_show_mode_options(updater, None)

    assert mock.called
    assert mock.call_args[0] == ('``` No saved filters found for this command ```',)
    assert data == ConversationHandler.END

    message = Message(1, timezone.now(), chat=None, text=BTN_CAPTION_CUSTOM_MGMT)
    chat = Chat(1, 'user')
    message.chat = chat
    updater.message = message
    data = c.get_mode_show_mode_options(updater, None)

    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == ConversationHandler.END


def test_get_mode_show_mode_options_w_f_and_c(mocker, telegram_bot):
    log = logging.getLogger()
    c = ConvTestFiltersCommands(log, suffix='dev')
    c.set_chat_id(1)

    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)
    mocker.patch('os.listdir', return_value=["x.py"])

    updater = Updater(bot=telegram_bot)
    message = Message(1, timezone.now(), chat=None, text=BTN_CAPTION_BUILD_QUERY)
    chat = Chat(1, 'user')
    message.chat = chat
    updater.message = message
    data = c.get_mode_show_mode_options(updater, None)

    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == TelegramConversation.STATUS.BUILD_PERIOD

    message = Message(1, timezone.now(), chat=None, text=BTN_CAPTION_USE_SAVED_FILTER)
    chat = Chat(1, 'user')
    message.chat = chat
    updater.message = message
    data = c.get_mode_show_mode_options(updater, None)

    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == TelegramConversation.STATUS.SAVED_FILTER_SELECT

    message = Message(1, timezone.now(), chat=None, text=BTN_CAPTION_CUSTOM_MGMT)
    chat = Chat(1, 'user')
    message.chat = chat
    updater.message = message
    data = c.get_mode_show_mode_options(updater, None)

    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == TelegramConversation.STATUS.CUSTOM_MGMT_COMMAND_SELECT


def test_get_period_uom_show_quantity(mocker, telegram_bot):
    log = logging.getLogger()
    c = ConvTest(log, suffix='dev')
    c.set_chat_id(1)

    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    updater = Updater(bot=telegram_bot)
    message = Message(1, timezone.now(), chat=None, text=WEEKS)
    chat = Chat(1, 'user')
    message.chat = chat
    updater.message = message
    data = c.get_period_uom_show_quantity(updater, None)

    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == TelegramConversation.STATUS.BUILD_PERIOD_QUANTITY
    assert c.query_period_uom == WEEKS


def test_show_list_of_commands(mocker, telegram_bot):
    log = logging.getLogger()
    c = ConvTest(log, suffix='dev')
    c.set_chat_id(1)

    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    updater = Updater(bot=telegram_bot)
    message = Message(1, timezone.now(), chat=None, text=WEEKS)
    chat = Chat(1, 'user')
    message.chat = chat
    updater.message = message
    data = c.show_list_of_commands(updater, None)

    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == ConversationHandler.END


def test_get_custom_command_and_execute(mocker, telegram_bot):
    log = logging.getLogger()
    c = ConvTest(log, suffix='dev')
    c.set_chat_id(1)
    c.model = MockModel

    def x(*args, **kwargs):
        #  empty function to patch custom mgmt command
        pass

    c.execute_custom_command = x

    mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)
    mocker.patch('os.listdir', return_value=["x.py"])

    updater = Updater(bot=telegram_bot)
    message = Message(1, timezone.now(), chat=None, text='x')
    chat = Chat(1, 'user')
    message.chat = chat
    updater.message = message
    data = c.get_custom_command_and_execute(updater, None)

    assert data == ConversationHandler.END
    assert c.custom_command == 'x'


def test_get_quantity_show_yes_no_filters(mocker, telegram_bot):
    log = logging.getLogger()
    c = ConvTest(log, suffix='dev')
    c.set_chat_id(1)

    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    updater = Updater(bot=telegram_bot)
    message = Message(1, timezone.now(), chat=None, text='10')
    chat = Chat(1, 'user')
    message.chat = chat
    updater.message = message
    data = c.get_quantity_show_yes_no_filters(updater, None)

    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == TelegramConversation.STATUS.BUILD_FILTERS_YES_NO
    assert c.query_period_quantity == 10


def test_execute_custom_command(telegram_bot, mocker):
    log = logging.getLogger()
    c = ConvTest(log, suffix='dev')
    c.set_chat_id(1)
    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)
    mocker.patch(
        'connect.telegram_bot.telegram_conversation.execute_from_command_line',
        return_value=True,
    )

    updater = Updater(bot=telegram_bot)
    message = Message(1, timezone.now(), chat=None, text='10')
    chat = Chat(1, 'user')
    message.chat = chat
    updater.message = message
    data = c.execute_custom_command(updater, 'command')

    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data is True
    assert c.query_context == {
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


def test_execute_custom_command_raise_exception(telegram_bot, mocker):
    log = logging.getLogger()
    c = ConvTest(log, suffix='dev')
    c.set_chat_id(1)
    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)
    mocker.patch(
        'connect.telegram_bot.telegram_conversation.execute_from_command_line',
        side_effect=Exception('error'),
    )

    updater = Updater(bot=telegram_bot)
    message = Message(1, timezone.now(), chat=None, text='10')
    chat = Chat(1, 'user')
    message.chat = chat
    updater.message = message
    data = c.execute_custom_command(updater, 'command')

    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data is False
    assert c.query_context == {
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


def test_get_yes_no_filters_and_proceed(mocker, telegram_bot):
    log = logging.getLogger()
    c = ConvTest(log, suffix='dev')
    c.set_chat_id(1)
    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    updater = Updater(bot=telegram_bot)
    message = Message(1, timezone.now(), chat=None, text=YES)
    chat = Chat(1, 'user')
    message.chat = chat
    updater.message = message
    data = c.get_yes_no_filters_and_proceed(updater, None)

    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == TelegramConversation.STATUS.BUILD_FILTERS

    message = Message(1, timezone.now(), chat=None, text=NO)
    chat = Chat(1, 'user')
    message.chat = chat
    updater.message = message
    data = c.get_yes_no_filters_and_proceed(updater, None)

    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == TelegramConversation.STATUS.BUILD_AGGREGATE_YES_NO


@pytest.mark.django_db(transaction=True)
def test_get_yes_no_aggregate_and_proceed(mocker, telegram_bot):
    log = logging.getLogger()
    c = ConvTest(log, suffix='dev')
    c.set_chat_id(1)
    c.set_query_period_uom(WEEKS)
    c.set_query_period_quantity(10)

    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    updater = Updater(bot=telegram_bot)
    message = Message(1, timezone.now(), chat=None, text=YES)
    chat = Chat(1, 'user')
    message.chat = chat
    updater.message = message
    data = c.get_yes_no_aggregate_and_proceed(updater, None)

    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == TelegramConversation.STATUS.BUILD_AGGREGATE

    fake_data = MockSet()
    for _i in range(1, 15):
        fake_data.add(MockModel(
            mock_name=f'name{_i}',
            id=f'id{_i}',
            name=f'name{_i}',
            status='pending',
            created_at=timezone.now(),
        ))

    mocker.patch(
        INITIAL_QUERY_SET_METHOD,
        return_value=fake_data,
    )

    message = Message(1, timezone.now(), chat=None, text=NO)
    chat = Chat(1, 'user')
    message.chat = chat
    updater.message = message
    data = c.get_yes_no_aggregate_and_proceed(updater, None)

    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == ConversationHandler.END


@pytest.mark.django_db(transaction=True)
def test_get_filters_and_proceed(mocker, telegram_bot):
    log = logging.getLogger()
    c = ConvTest(log, suffix='dev')
    c.set_chat_id(1)
    c.set_query_period_uom(WEEKS)
    c.set_query_period_quantity(10)

    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    updater = Updater(bot=telegram_bot)
    message = Message(1, timezone.now(), chat=None, text='status=succeeded')
    chat = Chat(1, 'user')
    message.chat = chat
    updater.message = message

    fake_data = MockSet()
    for _i in range(1, 15):
        fake_data.add(MockModel(
            mock_name=f'name{_i}',
            id=f'id{_i}',
            name=f'name{_i}',
            status='pending',
            created_at=timezone.now(),
        ))

    mocker.patch(
        INITIAL_QUERY_SET_METHOD,
        return_value=fake_data,
    )

    data = c.get_filters_and_proceed(updater, None)
    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == TelegramConversation.STATUS.BUILD_AGGREGATE_YES_NO
    assert c.query_filters == [{'status': 'succeeded'}]


@pytest.mark.django_db(transaction=True)
def test_get_aggregate_property_and_proceed(mocker, telegram_bot):
    log = logging.getLogger()
    c = ConvTest(log, suffix='dev')
    c.set_chat_id(1)
    c.set_query_period_uom(WEEKS)
    c.set_query_period_quantity(10)
    c.set_aggregate_type(SUM)

    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    updater = Updater(bot=telegram_bot)
    message = Message(1, timezone.now(), chat=None, text='id')
    chat = Chat(1, 'user')
    message.chat = chat
    updater.message = message

    fake_data = MockSet()
    for _i in range(1, 15):
        fake_data.add(MockModel(
            id=_i,
            name=f'name{_i}',
            status='pending',
            created_at=timezone.now(),
        ))

    mocker.patch(
        INITIAL_QUERY_SET_METHOD,
        return_value=fake_data,
    )

    data = c.get_aggregate_property_and_proceed(updater, None)
    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == ConversationHandler.END
    assert c.aggregate_property == 'id'


@pytest.mark.django_db(transaction=True)
def test_get_aggregate_and_proceed_count(mocker, telegram_bot):
    log = logging.getLogger()
    c = ConvTest(log, suffix='dev')
    c.set_query_period_uom(WEEKS)
    c.set_query_period_quantity(10)
    c.set_chat_id(1)

    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    updater = Updater(bot=telegram_bot)
    message = Message(1, timezone.now(), chat=None, text=COUNT)
    chat = Chat(1, 'user')
    message.chat = chat
    updater.message = message

    fake_data = MockSet()
    for _i in range(1, 15):
        fake_data.add(MockModel(
            mock_name=f'name{_i}',
            id=f'id{_i}',
            name=f'name{_i}',
            status='pending',
            created_at=timezone.now(),
        ))

    mocker.patch(
        INITIAL_QUERY_SET_METHOD,
        return_value=fake_data,
    )

    data = c.get_aggregate_and_proceed(updater, None)
    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == ConversationHandler.END
    assert c.aggregate_type == COUNT


@FakeModel.fake_me
@pytest.mark.django_db(transaction=True)
def test__get_initial_queryset():
    log = logging.getLogger()
    c = ConvTest(log, suffix='dev')
    c.model = FakeModel
    c.set_chat_id(1)

    data = c._get_initial_queryset()

    assert len(data) == 0


@FakeModel.fake_me
@pytest.mark.django_db(transaction=True)
def test_empty_queryset(mocker, telegram_bot):
    log = logging.getLogger()
    c = ConvTest(log, suffix='dev')
    c.model = FakeModel
    c.set_chat_id(1)
    c.set_query_period_uom(WEEKS)
    c.set_query_period_quantity(1)
    c.add_query_filter('status', 'pending')
    c.set_query_mode(BTN_CAPTION_BUILD_QUERY)

    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    updater = Updater(bot=telegram_bot)
    message = Message(1, timezone.now(), chat=None, text=COUNT)
    chat = Chat(1, 'user')
    message.chat = chat
    updater.message = message

    c.run_query(updater)

    assert mock.call_args[0] == (f'``` {TelegramConversation.EMPTY_RESULT} ```',)


def test_get_aggregate_and_proceed_sum(
        mocker, telegram_bot,
):
    log = logging.getLogger()
    c = ConvTest(log, suffix='dev')
    c.set_query_period_uom(WEEKS)
    c.set_query_period_quantity(10)
    c.set_chat_id(1)
    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    updater = Updater(bot=telegram_bot)
    message = Message(1, timezone.now(), chat=None, text=SUM)
    chat = Chat(1, 'user')
    message.chat = chat
    updater.message = message

    data = c.get_aggregate_and_proceed(updater, None)

    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == c.STATUS.BUILD_AGGREGATE_SUM_PROPERTY
    assert c.aggregate_type == SUM


def test_get_aggregate_and_proceed_unknown(
        mocker, telegram_bot,
):
    log = logging.getLogger()
    c = ConvTest(log, suffix='dev')
    c.set_query_period_uom(WEEKS)
    c.set_query_period_quantity(10)
    c.set_chat_id(1)
    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    updater = Updater(bot=telegram_bot)
    message = Message(1, timezone.now(), chat=None, text='unknown')
    chat = Chat(1, 'user')
    message.chat = chat
    updater.message = message

    data = c.get_aggregate_and_proceed(updater, None)

    assert mock.called
    assert mock.call_args[0] == ('``` End of conversation ```',)
    assert data == ConversationHandler.END


@pytest.mark.django_db(transaction=True)
def test_get_saved_filter_and_proceed(
        mocker, telegram_bot,
):
    log = logging.getLogger()
    c = ConvTest(log, suffix='dev')
    c.model = MockModel
    c.set_chat_id(1)
    c.get_saved_filter = lambda x: 1

    mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    updater = Updater(bot=telegram_bot)
    message = Message(1, timezone.now(), chat=None, text='saved_filter')
    chat = Chat(1, 'user')
    message.chat = chat
    updater.message = message

    data = c.get_saved_filter_and_proceed(updater, None)
    assert data == ConversationHandler.END
    assert c.saved_filter == 'saved_filter'


@pytest.mark.django_db(transaction=True)
def test_get_saved_filter_and_proceed_no_filter_method(
        mocker, telegram_bot,
):
    log = logging.getLogger()
    c = ConvTest(log, suffix='dev')
    c.model = MockModel
    c.set_chat_id(1)
    mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    updater = Updater(bot=telegram_bot)
    message = Message(1, timezone.now(), chat=None, text='unknown')
    chat = Chat(1, 'user')
    message.chat = chat
    updater.message = message

    with pytest.raises(SavedFilterNotFound):
        c.get_saved_filter_and_proceed(updater, None)


@pytest.mark.django_db(transaction=True)
def test_get_saved_filter_and_proceed_no_user(
        mocker, telegram_bot,
):
    log = logging.getLogger()
    c = ConvTest(log, suffix='dev')
    c.model = MockModel
    c.get_saved_filter = lambda x: 1
    mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    updater = Updater(bot=telegram_bot)
    message = Message(1, timezone.now(), chat=None, text='saved_filter')
    chat = Chat(1, 'user')
    message.chat = chat
    updater.message = message

    data = c.get_saved_filter_and_proceed(updater, None)
    assert data is None


def test_invalid_suffix():
    with pytest.raises(ValueError):
        ConvTest(object, '-dev')
