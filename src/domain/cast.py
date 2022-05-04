import time
from typing import List

import attr

from ctx.player import PlayerStateManager, Player
from domain.game.control import Key, Keys
from domain.game.game import Game
from domain.task import Task, StoppableThread


@attr.s(slots=True)
class Cast:
    key = attr.ib(type=Key)
    min_mana = attr.ib(type=int, kw_only=True)
    min_health = attr.ib(type=int, kw_only=True)
    priority = attr.ib(type=int, default=0, kw_only=True)
    delay = attr.ib(type=float, default=0.2, kw_only=True)

    def should_cast(self, player: Player):
        raise NotImplementedError()

    @classmethod
    def deserialize(cls, cfg: dict):
        key = cfg['key']
        cfg = cfg.copy()
        cfg['key'] = Keys.from_str(key)
        return cls(**cfg)


@attr.s
class Caster(Task):
    game = attr.ib(type=Game)
    psm = attr.ib(type=PlayerStateManager)
    cast_list = attr.ib(type=List[Cast])
    delay = attr.ib(type=float, default=0.1, kw_only=True)

    def __attrs_post_init__(self):
        self.cast_list = sorted(self.cast_list, key=lambda c: (c.priority, c.min_health, c.min_mana))

    def _run(self):
        self.thread = StoppableThread(target=self._cast, args=(), daemon=True)
        self.thread.start()

    def _cast(self):
        while not self.thread.stopped():
            player: Player = self.psm.get().value
            if not self.game.is_connected() or not player:
                time.sleep(self.delay)
                continue
            for cast in self.cast_list:
                if not cast.should_cast(player):
                    time.sleep(self.delay)
                    continue
                controller = self.game.controller
                controller.press(cast.key)
                if cast.delay:
                    time.sleep(cast.delay)
                break
