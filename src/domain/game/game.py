from typing import List

import attr
import win32gui
from pynput.keyboard import Listener, Key

from domain.task import Task


@attr.s
class Game:
    name = attr.ib(default='Tibia', type=str, init=True, kw_only=False)
    tasks = attr.ib(init=False, type=List[Task], factory=list)
    exit_key = attr.ib(init=False, default=Key.pause, kw_only=True)
    exit_listener = attr.ib(init=False)

    def is_active(self):
        w = win32gui
        return w.GetWindowText(w.GetForegroundWindow()) == self.name

    def add_task(self, task: Task):
        self.tasks.append(task)

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

    def await_exit(self):
        with Listener(on_release=self._on_release) as listener:
            self.exit_listener = listener
            listener.join()
