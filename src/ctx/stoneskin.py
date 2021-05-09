import time

import attr
import pynput

from ctx.player import PlayerStateManager, Player
from domain.game.game import Game
from domain.task import Task, StoppableThread


@attr.s
class StoneSkinTask(Task):
    game = attr.ib(type=Game)
    psm = attr.ib(type=PlayerStateManager)
    key = attr.ib(init=True, type=pynput.keyboard.Key, kw_only=True)
    equip_at = attr.ib(type=int)
    delay = attr.ib(type=float, default=0.4, kw_only=True)

    def _run(self):
        self.thread = StoppableThread(target=self._equip, args=(), daemon=True)
        self.thread.start()

    def _equip(self):
        while not self.thread.stopped():
            player: Player = self.psm.get().value
            if not self.game.is_active() or not player:
                time.sleep(self.delay)
                continue
            if player.health < self.equip_at:
                self.keyboard.press(self.key)
                self.keyboard.release(self.key)
                if self.delay:
                    time.sleep(self.delay)
            else:
                time.sleep(0.5)
