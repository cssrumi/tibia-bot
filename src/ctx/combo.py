import time
from itertools import cycle
from typing import List, Union

import attr
from pynput.keyboard import Key, Listener

from ctx.player import PlayerStateManager, Player
from domain.cast import Cast
from domain.game.game import Game
from domain.task import Task, StoppableThread


@attr.s
class AttackSpell(Cast):
    min_mana = attr.ib(type=int, kw_only=True, default=0)
    min_health = attr.ib(type=int, kw_only=True, default=0)

    def should_cast(self, player: Player):
        return player.health >= self.min_health and player.mana >= self.min_mana


@attr.s
class AttackRune(Cast):
    min_mana = attr.ib(type=int, kw_only=True, default=100)
    min_health = attr.ib(type=int, kw_only=True, default=100)

    def should_cast(self, player: Player):
        return True


@attr.s
class ComboCaster(Task):
    game = attr.ib(type=Game)
    psm = attr.ib(type=PlayerStateManager)
    cast_list = attr.ib(type=List[Cast])
    delay = attr.ib(type=float, default=0.2, kw_only=True)
    is_stopped = attr.ib(type=bool, default=True)

    def __attrs_post_init__(self):
        self.game.add_task(self)

    def _run(self):
        self.thread = StoppableThread(target=self._combo, args=(), daemon=True)
        self.thread.start()

    def switch(self):
        self.is_stopped = not self.is_stopped

    def _combo(self):
        while not self.thread.stopped():
            player: Player = self.psm.get().value
            if not self.game.is_active() or not player or self.is_stopped:
                time.sleep(self.delay)
                continue
            for cast in cycle(self.cast_list):
                if cast.should_cast(player):
                    self.keyboard.press(cast.key)
                    self.keyboard.release(cast.key)
                if self.is_stopped:
                    break
                if cast.cooldown:
                    time.sleep(cast.cooldown)


@attr.s
class ComboSwitch:
    combo_caster = attr.ib(type=ComboCaster)
    key = attr.ib(type=Union[Key, str])
    _listener = attr.ib(init=False, type=Listener)

    def __attrs_post_init__(self):
        self._listen()

    def _listen(self):
        listener = Listener(on_release=self._on_release)
        listener.start()
        self._listener = listener
        self.combo_caster.game.register_on_exit(self._stop)

    def _stop(self):
        print("stopping combo listener")
        self._listener.stop()

    def _on_release(self, key: Union[Key, str]):
        if key == self.key:
            self.combo_caster.switch()
            off_on = "off" if self.combo_caster.is_stopped else "on"
            print("combo turn", off_on)
