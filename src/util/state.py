import time
from typing import TypeVar, Generic, Callable, List

import attr

from app.logger import Logger
from util.task import Task, StoppableThread

T = TypeVar("T")


@attr.s
class State(Generic[T]):
    value = attr.ib(type=T, default=None)

    def get(self):
        return self.value

    def is_empty(self) -> bool:
        return not bool(self.value)


@attr.s
class StateManager(Generic[T]):
    _state = attr.ib(type=State[T], factory=State, init=False)
    listeners = attr.ib(type=List[Callable[[T], None]], factory=list, init=False, kw_only=True)

    def get(self) -> State[T]:
        return self._state

    def update(self, new_value: T) -> T:
        self._state.value = new_value
        [listener(self._state) for listener in self.listeners]
        # print(f"{self.__class__.__name__} state updated")
        return new_value

    def add_update_listener(self, listener: Callable[[State[T]], None]):
        self.listeners.append(listener)


@attr.s
class StateManagerTask(Task, StateManager[T], Generic[T]):
    game = attr.ib()
    delay = attr.ib(type=float, default=0.0, kw_only=True)
    on_active_only = attr.ib(type=bool, default=False, kw_only=True)

    def _run(self):
        self.thread = StoppableThread(target=self.executor, args=(), daemon=True)
        self.thread.start()

    def executor(self):
        while not self.thread.stopped():
            start = int(time.time_ns())
            if self.game.is_active() or not self.on_active_only:
                self.update(self.new_value())
                if self.delay:
                    time.sleep(self.delay)
                end_ = int((time.time_ns()) - start) / 1_000_000
                Logger.debug(f"Total state execution time of {self.__class__.__name__}: {end_ if end_ > 0 else 0} ms")
            else:
                time.sleep(0.5)

    def new_value(self) -> T:
        raise NotImplementedError()
