import time

import attr
import pynput

from state.game import Game
from task.task import Task, StoppableThread


@attr.s
class FoodEater(Task):
    game = attr.ib(init=True, type=Game)
    key = attr.ib(init=True, type=pynput.keyboard.Key, kw_only=True)
    delay = attr.ib(init=False, kw_only=True, type=float, default=5)

    def _start(self):
        self.thread = StoppableThread(target=self._eat_food, args=(), daemon=True)
        self.thread.start()

    def _eat_food(self):
        while not self.thread.stopped():
            if self.game.is_active():
                self.keyboard.press(self.key)
                self.keyboard.release(self.key)
                time.sleep(self.delay)
            time.sleep(0.5)
