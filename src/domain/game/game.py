import time
from typing import List, Callable

import attr
import win32gui
from pynput.keyboard import Listener, Key
from pywinauto import Application

from domain.task import Task


@attr.s
class Game:
    name = attr.ib(default='Tibia', type=str, kw_only=False)
    tasks = attr.ib(init=False, type=List[Task], factory=list)
    _on_exit = attr.ib(init=False, type=List[Callable], factory=list)
    app = attr.ib(kw_only=True, type=Application, factory=Application)
    exit_key = attr.ib(init=False, default=Key.pause, kw_only=True)
    exit_listener = attr.ib(init=False)
    _is_connected = attr.ib(init=False, type=bool, default=False)

    def __attrs_post_init__(self):
        self.add_task(AppConnectTask(self))

    def is_active(self):
        w = win32gui
        return w.GetWindowText(w.GetForegroundWindow()) == self.name

    def is_connected(self):
        return self._is_connected

    def add_task(self, task: Task):
        self.tasks.append(task)

    def remove_task(self, task: Task):
        self.tasks.remove(task)
        print(task.__class__, "removed")

    def start_all(self):
        [task.start() for task in self.tasks]

    def stop_all(self):
        print("Application shutdown...")
        [task.stop() for task in self.tasks]
        while any(task.is_started() for task in self.tasks):
            pass
        self.exit_listener.stop()

    def _on_release(self, key: Key):
        if key == self.exit_key:
            self.stop_all()
            [fun() for fun in self._on_exit]

    def await_exit(self):
        with Listener(on_release=self._on_release) as listener:
            self.exit_listener = listener
            listener.join()

    def register_on_exit(self, function: Callable):
        self._on_exit.append(function)


@attr.s
class AppConnectTask(Task):
    game = attr.ib(type=Game)
    app = attr.ib(init=False, type=Application)
    _is_connected = attr.ib(init=False, type=bool, default=False)

    def __attrs_post_init__(self):
        self.app = self.game.app

    def _connect(self) -> bool:
        if self._is_connected or not self.game.is_active():
            return False
        self.app.connect(title=self.game.name)
        self._is_connected = True
        self.game._is_connected = True
        print('Connected to Tibia application')
        return True

    def _run(self):
        while not self._is_connected:
            self._connect()
            time.sleep(1)
            continue
        self.stop()
        self.game.tasks.remove(self)

