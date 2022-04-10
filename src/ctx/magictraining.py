import time

import attr

from ctx.player import PlayerStateManager
from domain.game.control import Key
from domain.game.game import Game
from domain.task import Task, StoppableThread


@attr.s
class MagicTrainingTask(Task):
    game = attr.ib(type=Game)
    psm = attr.ib(type=PlayerStateManager)
    key = attr.ib(type=Key, kw_only=True)
    min_mana = attr.ib(kw_only=True, type=int)
    min_health = attr.ib(kw_only=True, type=int, default=100)
    delay = attr.ib(init=False, kw_only=True, type=float, default=1)

    def __attrs_post_init__(self):
        self.game.add_task(self)

    def _run(self):
        self.thread = StoppableThread(target=self._train, args=(), daemon=True)
        self.thread.start()

    def _train(self):
        while not self.thread.stopped():
            player = self.psm.get().value
            if self.game.is_connected() and player and player.mana >= self.min_mana and player.health >= self.min_health:
                controller = self.game.controller
                controller.press(self.key)
                if self.delay:
                    time.sleep(self.delay)
            else:
                time.sleep(0.5)
