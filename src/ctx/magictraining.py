import time

import attr
import pynput

from ctx.player import PlayerStateManager
from domain.game.game import Game
from domain.task import Task, StoppableThread


@attr.s
class MagicTrainingTask(Task):
    game = attr.ib(init=True, type=Game)
    psm = attr.ib(init=True, type=PlayerStateManager)
    key = attr.ib(init=True, type=pynput.keyboard.Key, kw_only=True)
    min_mana = attr.ib(init=True, kw_only=True, type=int)
    min_health = attr.ib(init=True, kw_only=True, type=int, default=100)
    delay = attr.ib(init=False, kw_only=True, type=float, default=1)

    def _run(self):
        self.thread = StoppableThread(target=self._train, args=(), daemon=True)
        self.thread.start()

    def _train(self):
        while not self.thread.stopped():
            player = self.psm.get().value
            if self.game.is_active() and player and player.mana >= self.min_mana and player.health >= self.min_health:
                self.keyboard.press(self.key)
                self.keyboard.release(self.key)
                if self.delay:
                    time.sleep(self.delay)
            else:
                time.sleep(0.5)
