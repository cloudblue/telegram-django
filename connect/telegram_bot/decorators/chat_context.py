from functools import wraps


def chat_context(func):
    @wraps(func)
    def check_chat_and_exec(self, update, context):
        if self.chat_id == update.message.chat.id:
            res = func(self, update, context)
            return res

    return check_chat_and_exec
