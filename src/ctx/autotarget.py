import time

import attr

from domain.game.control import Key, Keys
from domain.game.game import Game
from domain.task import Task, StoppableThread


@attr.s
class AutoTargetTask(Task):
    game = attr.ib(type=Game)
    key = attr.ib(init=False, default=Keys.SPACE, type=Key)
    delay = attr.ib(init=False, kw_only=True, type=float, default=0.5)

    def __attrs_post_init__(self):
        self.game.add_task(self)

    def _run(self):
        self.thread = StoppableThread(target=self._eat_food, args=(), daemon=True)
        self.thread.start()

    def _eat_food(self):
        while not self.thread.stopped():
            if self.game.is_active():
                self.game.controller.press(self.key)
                time.sleep(self.delay)
            time.sleep(0.5)
