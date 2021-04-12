from typing import TypeVar, Generic

import attr

from state import State

T = TypeVar("T")


@attr.s
class Listener(Generic[T]):
    priority = attr.ib(type=int, default=0, kw_only=True, init=True)

    def update_listener(self, state: State[T]) -> None:
        raise NotImplementedError()
