import time
from itertools import cycle
from typing import List

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
    delay = attr.ib(type=float, default=0.1, kw_only=True)
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
                if self.is_stopped:
                    break
                if cast.should_cast(player):
                    self.keyboard.press(cast.key)
                    self.keyboard.release(cast.key)
                if cast.cooldown:
                    time.sleep(cast.cooldown)
                if self.delay:
                    time.sleep(self.delay)


@attr.s
class ComboSwitch(Task):
    combo_caster = attr.ib(type=ComboCaster)
    key = attr.ib(type=Key)
    _listener = attr.ib(init=False, type=Listener)

    def __attrs_post_init__(self):
        self.combo_caster.game.add_task(self)

    def _run(self):
        self.thread = StoppableThread(target=self._listen, args=(), daemon=True)
        self.thread.start()

    def _listen(self):
        self.combo_caster.game.register_on_exit(self._stop_listener)
        with Listener(on_release=self._on_release) as listener:
            self._listener = listener
            listener.join()

    def _stop_listener(self):
        print("stopping combo listener")
        if self._listener:
            self._listener.stop()

    def _on_release(self, key: Key):
        if key == self.key:
            self.combo_caster.switch()
            off_on = "off" if self.combo_caster.is_stopped else "on"
            print("combo turn", off_on)
