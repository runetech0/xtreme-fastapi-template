from typing import cast

from fastapi import Request

from redis_handlers.dispatcher import Dispatcher


def get_dispatcher(request: Request) -> Dispatcher:
    return cast(Dispatcher, request.app.state.dispatcher)
