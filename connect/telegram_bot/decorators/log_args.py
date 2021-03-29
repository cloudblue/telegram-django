from functools import wraps


def log_args(func):
    @wraps(func)
    def log_and_exec(self, update, context):
        self.logger.info(f'Input: {func.__name__}: {update.message.text}')
        res = func(self, update, context)
        self.logger.info(f'Output: {func.__name__}: {res}')
        return res

    return log_and_exec
