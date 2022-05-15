import threading
import time

import attr

from app.logger import Logger
from util.switch import Switchable


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


@attr.s
class Task:
    name = attr.ib(default=attr.Factory(lambda self: self.__class__.__name__, takes_self=True), init=False)
    thread = attr.ib(default=None, type=StoppableThread, init=False)

    def start(self):
        if self.is_started():
            return
        self._run()
        Logger.debug(f"{self.name} started!")

    def _run(self):
        raise NotImplementedError()

    def is_started(self):
        return self.thread.is_alive() if self.thread else False

    def stop(self):
        if self.thread:
            self.thread.stop()


@attr.s
class RepeatableTask(Task, Switchable):
    switch_delay = attr.ib(type=float, kw_only=True, default=0.5)
    condition_delay = attr.ib(type=float, kw_only=True, default=1)
    action_delay = attr.ib(type=float, kw_only=True, default=1)

    def _run(self):
        self.thread = StoppableThread(target=self._loop, args=(), daemon=True)
        self.thread.start()

    def _loop(self):
        while not self.thread.stopped():
            if self.is_stopped:
                time.sleep(self.switch_delay)
                continue
            if self._skip_condition():
                time.sleep(self.condition_delay)
                continue
            self._action()
            time.sleep(self.action_delay)

    def _skip_condition(self) -> bool:
        raise NotImplementedError()

    def _action(self):
        raise NotImplementedError()
