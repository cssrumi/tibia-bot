import threading

import attr
from pynput.keyboard import Controller


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
    keyboard = attr.ib(default=Controller(), type=Controller, init=False, kw_only=True)

    def start(self):
        if self.is_started():
            return
        self._run()
        print(f"{self.name} started!")

    def _run(self):
        raise NotImplementedError()

    def is_started(self):
        return self.thread.is_alive() if self.thread else False

    def stop(self):
        if self.thread:
            self.thread.stop()
