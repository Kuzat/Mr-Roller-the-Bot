import asyncio
from functools import wraps


def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_running_loop()
            return loop.create_task(f(*args, **kwargs))
        except RuntimeError:  # 'RuntimeError: There is no current event loop...'
            return asyncio.run(f(*args, **kwargs))

    return wrapper
