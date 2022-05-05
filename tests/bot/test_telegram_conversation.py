import logging

import pytest
from django.utils import timezone
from django_mock_queries.query import MockModel, MockSet
from telegram import Chat, Message, Update
from telegram.ext import ConversationHandler


from django_telegram.bot.constants import (
    BTN_CAPTION_BUILD_QUERY, BTN_CAPTION_CUSTOM_MGMT, BTN_CAPTION_USE_SAVED_FILTER,
    COUNT, NO, SUM, WEEKS, YES,
)
from django_telegram.bot.errors.saved_filter_not_found import SavedFilterNotFound
from django_telegram.bot.telegram_conversation import TelegramConversation
from tests.bot import DJANGO_CALL_COMMAND, INITIAL_QUERY_SET_METHOD, TELEGRAM_REPLY_METHOD
from tests.bot.conftest import ConvTest, ConvTestFiltersCommands, FakeModel


def test_conversation_handler():
    log = logging.getLogger()
    c = ConvTest(log, 'created_at', suffix='dev')

    handler = c.get_conversation_handler()
    entry_point = handler.entry_points[0]
    fallback = handler.fallbacks[0]

    assert len(handler.states) == 10
    assert entry_point.command == [f'{c.__class__.__name__.lower()}_dev']
    assert fallback.command == ['cancel_dev']


def test_conversation_handler_no_suffix():
    log = logging.getLogger()
    c = ConvTest(log, 'created_at')

    handler = c.get_conversation_handler()
    entry_point = handler.entry_points[0]
    fallback = handler.fallbacks[0]

    assert len(handler.states) == 10
    assert entry_point.command == [c.__class__.__name__.lower()]
    assert fallback.command == ['cancel']


def test_conversation_handler_custom_fb_and_entry():
    log = logging.getLogger()
    c = ConvTest(log, 'created_at', suffix='dev')
    c.set_entrypoint_name('test_start')
    c.set_fallback_name('test_end')

    handler = c.get_conversation_handler()
    entry_point = handler.entry_points[0]
    fallback = handler.fallbacks[0]

    assert len(handler.states) == 10
    assert entry_point.command == ['test_start']
    assert fallback.command == ['test_end']


def test_cancel(mocker):
    log = logging.getLogger()
    c = ConvTest(log, 'created_at', suffix='dev')
    c.set_chat_id(1)

    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    update = Update(1)
    chat = Chat(1, 'user')
    message = Message(1, timezone.now(), chat=chat)
    message.chat = chat
    update.message = message
    data = c.cancel(update, None)

    assert mock.called
    assert mock.call_args[0] == ('``` End of conversation ```',)
    assert data == ConversationHandler.END


def test_show_mode_select(mocker):
    log = logging.getLogger()
    c = ConvTest(log, 'created_at', suffix='dev')
    c.set_chat_id(1)

    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    update = Update(1)
    chat = Chat(1, 'user')
    message = Message(1, timezone.now(), chat=chat)
    message.chat = chat
    update.message = message
    data = c.show_mode_select(update, None)

    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == TelegramConversation.STATUS.MODE_SELECTOR


def test_get_mode_show_mode_options(mocker):
    log = logging.getLogger()
    c = ConvTest(log, 'created_at', suffix='dev')
    c.set_chat_id(1)

    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    update = Update(1)
    chat = Chat(1, 'user')
    message = Message(1, timezone.now(), chat=chat, text=BTN_CAPTION_BUILD_QUERY)
    message.chat = chat
    update.message = message
    data = c.get_mode_show_mode_options(update, None)

    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == TelegramConversation.STATUS.BUILD_PERIOD

    message = Message(1, timezone.now(), chat=chat, text=BTN_CAPTION_USE_SAVED_FILTER)
    message.chat = chat
    update.message = message
    data = c.get_mode_show_mode_options(update, None)

    assert mock.called
    assert mock.call_args[0] == ('``` No saved filters found for this command ```',)
    assert data == ConversationHandler.END

    message = Message(1, timezone.now(), chat=chat, text=BTN_CAPTION_CUSTOM_MGMT)
    message.chat = chat
    update.message = message
    data = c.get_mode_show_mode_options(update, None)

    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == ConversationHandler.END


def test_get_mode_show_mode_options_w_f_and_c(mocker):
    log = logging.getLogger()
    c = ConvTestFiltersCommands(log, 'created_at', suffix='dev')
    c.set_chat_id(1)

    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)
    mocker.patch('os.listdir', return_value=["x.py"])

    update = Update(1)
    chat = Chat(1, 'user')
    message = Message(1, timezone.now(), chat=chat, text=BTN_CAPTION_BUILD_QUERY)
    message.chat = chat
    update.message = message
    data = c.get_mode_show_mode_options(update, None)

    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == TelegramConversation.STATUS.BUILD_PERIOD

    message = Message(1, timezone.now(), chat=chat, text=BTN_CAPTION_USE_SAVED_FILTER)
    message.chat = chat
    update.message = message
    data = c.get_mode_show_mode_options(update, None)

    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == TelegramConversation.STATUS.SAVED_FILTER_SELECT

    message = Message(1, timezone.now(), chat=chat, text=BTN_CAPTION_CUSTOM_MGMT)
    message.chat = chat
    update.message = message
    data = c.get_mode_show_mode_options(update, None)

    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == TelegramConversation.STATUS.CUSTOM_MGMT_COMMAND_SELECT


def test_get_period_uom_show_quantity(mocker):
    log = logging.getLogger()
    c = ConvTest(log, 'created_at', suffix='dev')
    c.set_chat_id(1)

    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    update = Update(1)
    chat = Chat(1, 'user')
    message = Message(1, timezone.now(), chat=chat, text=WEEKS)
    message.chat = chat
    update.message = message
    data = c.get_period_uom_show_quantity(update, None)

    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == TelegramConversation.STATUS.BUILD_PERIOD_QUANTITY
    assert c.query_period_uom == WEEKS


def test_show_list_of_commands(mocker):
    log = logging.getLogger()
    c = ConvTest(log, 'created_at', suffix='dev')
    c.set_chat_id(1)

    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    update = Update(1)
    chat = Chat(1, 'user')
    message = Message(1, timezone.now(), chat=chat, text=WEEKS)
    message.chat = chat
    update.message = message
    data = c.show_list_of_commands(update, None)

    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == ConversationHandler.END


def test_get_custom_command_and_execute(mocker):
    log = logging.getLogger()
    c = ConvTest(log, 'created_at', suffix='dev')
    c.set_chat_id(1)
    c.model = MockModel

    def x(*args, **kwargs):
        #  empty function to patch custom mgmt command
        pass

    c.execute_custom_command = x

    mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)
    mocker.patch('os.listdir', return_value=["x.py"])

    update = Update(1)
    chat = Chat(1, 'user')
    message = Message(1, timezone.now(), chat=chat, text='x')
    message.chat = chat
    update.message = message
    data = c.get_custom_command_and_execute(update, None)

    assert data == ConversationHandler.END
    assert c.custom_command == 'x'


def test_get_quantity_show_yes_no_filters(mocker):
    log = logging.getLogger()
    c = ConvTest(log, 'created_at', suffix='dev')
    c.set_chat_id(1)

    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    update = Update(1)
    chat = Chat(1, 'user')
    message = Message(1, timezone.now(), chat=chat, text='10')
    message.chat = chat
    update.message = message
    data = c.get_quantity_show_yes_no_filters(update, None)

    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == TelegramConversation.STATUS.BUILD_FILTERS_YES_NO
    assert c.query_period_quantity == 10


def test_execute_command_exception(mocker):
    log = logging.getLogger()
    c = ConvTestFiltersCommands(log, 'created_at', suffix='dev')
    c.set_chat_id(1)
    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)
    mocker.patch(
        DJANGO_CALL_COMMAND,
        side_effect=Exception('ERROR'),
    )

    update = Update(1)
    chat = Chat(1, 'user')
    message = Message(1, timezone.now(), chat=chat, text='10')
    message.chat = chat
    update.message = message
    data = c.execute_custom_command(update, 'xx')
    assert mock.called
    assert mock.call_args[0] == ("``` Error xx:\nERROR ```",)
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


def test_execute_custom_command(mocker):
    log = logging.getLogger()
    c = ConvTestFiltersCommands(log, 'created_at', suffix='dev')
    c.set_chat_id(1)
    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)
    mocker.patch(
        DJANGO_CALL_COMMAND,
        return_value=True,
    )

    update = Update(1)
    chat = Chat(1, 'user')
    message = Message(1, timezone.now(), chat=chat, text='10')
    message.chat = chat
    update.message = message
    data = c.execute_custom_command(update, 'xx')

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


def test_execute_custom_command_raise_exception(mocker):
    log = logging.getLogger()
    c = ConvTest(log, 'created_at', suffix='dev')
    c.set_chat_id(1)
    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)
    mocker.patch(
        DJANGO_CALL_COMMAND,
        side_effect=Exception('error'),
    )

    update = Update(1)
    chat = Chat(1, 'user')
    message = Message(1, timezone.now(), chat=chat, text='10')
    message.chat = chat
    update.message = message
    data = c.execute_custom_command(update, 'command')

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


def test_get_yes_no_filters_and_proceed(mocker):
    log = logging.getLogger()
    c = ConvTest(log, 'created_at', suffix='dev')
    c.set_chat_id(1)
    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    update = Update(1)
    chat = Chat(1, 'user')
    message = Message(1, timezone.now(), chat=chat, text=YES)
    message.chat = chat
    update.message = message
    data = c.get_yes_no_filters_and_proceed(update, None)

    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == TelegramConversation.STATUS.BUILD_FILTERS

    message = Message(1, timezone.now(), chat=chat, text=NO)
    message.chat = chat
    update.message = message
    data = c.get_yes_no_filters_and_proceed(update, None)

    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == TelegramConversation.STATUS.BUILD_AGGREGATE_YES_NO


@pytest.mark.django_db(transaction=True)
def test_get_yes_no_aggregate_and_proceed(mocker):
    log = logging.getLogger()
    c = ConvTest(log, 'created_at', suffix='dev')
    c.set_chat_id(1)
    c.set_query_period_uom(WEEKS)
    c.set_query_period_quantity(10)

    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    update = Update(1)
    chat = Chat(1, 'user')
    message = Message(1, timezone.now(), chat=chat, text=YES)
    message.chat = chat
    update.message = message
    data = c.get_yes_no_aggregate_and_proceed(update, None)

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

    message = Message(1, timezone.now(), chat=chat, text=NO)
    message.chat = chat
    update.message = message
    data = c.get_yes_no_aggregate_and_proceed(update, None)

    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == ConversationHandler.END


@pytest.mark.django_db(transaction=True)
def test_get_filters_and_proceed(mocker):
    log = logging.getLogger()
    c = ConvTest(log, 'created_at', suffix='dev')
    c.set_chat_id(1)
    c.set_query_period_uom(WEEKS)
    c.set_query_period_quantity(10)

    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    update = Update(1)
    chat = Chat(1, 'user')
    message = Message(1, timezone.now(), chat=chat, text='status=succeeded')
    message.chat = chat
    update.message = message

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

    data = c.get_filters_and_proceed(update, None)
    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == TelegramConversation.STATUS.BUILD_AGGREGATE_YES_NO
    assert c.query_filters == [{'status': 'succeeded'}]


@pytest.mark.django_db(transaction=True)
def test_get_aggregate_property_and_proceed(mocker):
    log = logging.getLogger()
    c = ConvTest(log, 'created_at', suffix='dev')
    c.set_chat_id(1)
    c.set_query_period_uom(WEEKS)
    c.set_query_period_quantity(10)
    c.set_aggregate_type(SUM)

    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    update = Update(1)
    chat = Chat(1, 'user')
    message = Message(1, timezone.now(), chat=chat, text='id')
    message.chat = chat
    update.message = message

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

    data = c.get_aggregate_property_and_proceed(update, None)
    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == ConversationHandler.END
    assert c.aggregate_property == 'id'


@pytest.mark.django_db(transaction=True)
def test_get_aggregate_and_proceed_count(mocker):
    log = logging.getLogger()
    c = ConvTest(log, 'created_at', suffix='dev')
    c.set_query_period_uom(WEEKS)
    c.set_query_period_quantity(10)
    c.set_chat_id(1)

    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    update = Update(1)
    chat = Chat(1, 'user')
    message = Message(1, timezone.now(), chat=chat, text=COUNT)
    message.chat = chat
    update.message = message

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

    data = c.get_aggregate_and_proceed(update, None)
    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == ConversationHandler.END
    assert c.aggregate_type == COUNT


@FakeModel.fake_me
@pytest.mark.django_db(transaction=True)
def test__get_initial_queryset():
    log = logging.getLogger()
    c = ConvTest(log, 'created_at', suffix='dev')
    c.model = FakeModel
    c.set_chat_id(1)

    data = c._get_initial_queryset()

    assert len(data) == 0


@FakeModel.fake_me
@pytest.mark.django_db(transaction=True)
def test_empty_queryset(mocker):
    log = logging.getLogger()
    c = ConvTest(log, 'created_at', suffix='dev')
    c.model = FakeModel
    c.set_chat_id(1)
    c.set_query_period_uom(WEEKS)
    c.set_query_period_quantity(1)
    c.add_query_filter('status', 'pending')
    c.set_query_mode(BTN_CAPTION_BUILD_QUERY)

    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    update = Update(1)
    chat = Chat(1, 'user')
    message = Message(1, timezone.now(), chat=chat, text=COUNT)
    message.chat = chat
    update.message = message

    c.run_query(update)

    assert mock.call_args[0] == (f'``` {TelegramConversation.EMPTY_RESULT} ```',)


def test_get_aggregate_and_proceed_sum(mocker):
    log = logging.getLogger()
    c = ConvTest(log, 'created_at', suffix='dev')
    c.set_query_period_uom(WEEKS)
    c.set_query_period_quantity(10)
    c.set_chat_id(1)
    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    update = Update(1)
    chat = Chat(1, 'user')
    message = Message(1, timezone.now(), chat=chat, text=SUM)
    message.chat = chat
    update.message = message

    data = c.get_aggregate_and_proceed(update, None)

    assert mock.called
    assert mock.call_args[0] != (f'``` {TelegramConversation.EMPTY_RESULT} ```',)
    assert data == c.STATUS.BUILD_AGGREGATE_SUM_PROPERTY
    assert c.aggregate_type == SUM


def test_get_aggregate_and_proceed_unknown(mocker):
    log = logging.getLogger()
    c = ConvTest(log, 'created_at', suffix='dev')
    c.set_query_period_uom(WEEKS)
    c.set_query_period_quantity(10)
    c.set_chat_id(1)
    mock = mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    update = Update(1)
    chat = Chat(1, 'user')
    message = Message(1, timezone.now(), chat=chat, text='unknown')
    message.chat = chat
    update.message = message

    data = c.get_aggregate_and_proceed(update, None)

    assert mock.called
    assert mock.call_args[0] == ('``` End of conversation ```',)
    assert data == ConversationHandler.END


@pytest.mark.django_db(transaction=True)
def test_get_saved_filter_and_proceed(mocker):
    log = logging.getLogger()
    c = ConvTest(log, 'created_at', suffix='dev')
    c.model = MockModel
    c.set_chat_id(1)
    c.get_saved_filter = lambda x: 1

    mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    update = Update(1)
    chat = Chat(1, 'user')
    message = Message(1, timezone.now(), chat=chat, text='saved_filter')
    message.chat = chat
    update.message = message

    data = c.get_saved_filter_and_proceed(update, None)
    assert data == ConversationHandler.END
    assert c.saved_filter == 'saved_filter'


@pytest.mark.django_db(transaction=True)
def test_get_saved_filter_and_proceed_no_filter_method(mocker):
    log = logging.getLogger()
    c = ConvTest(log, 'created_at', suffix='dev')
    c.model = MockModel
    c.set_chat_id(1)
    mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    update = Update(1)
    chat = Chat(1, 'user')
    message = Message(1, timezone.now(), chat=chat, text='unknown')
    message.chat = chat
    update.message = message

    with pytest.raises(SavedFilterNotFound):
        c.get_saved_filter_and_proceed(update, None)


@pytest.mark.django_db(transaction=True)
def test_get_saved_filter_and_proceed_no_user(mocker):
    log = logging.getLogger()
    c = ConvTest(log, 'created_at', suffix='dev')
    c.model = MockModel
    c.get_saved_filter = lambda x: 1
    mocker.patch(TELEGRAM_REPLY_METHOD, return_value=None)

    chat = Chat(1, 'user')
    message = Message(1, timezone.now(), chat=chat, text='saved_filter')
    message.chat = chat
    update = Update(1)
    update.message = message
    data = c.get_saved_filter_and_proceed(update, None)
    assert data is None


def test_invalid_suffix():
    with pytest.raises(ValueError):
        ConvTest(object, 'created_at', '-dev')
