import time
from itertools import cycle
from typing import List

import attr
from pynput.keyboard import Key as PPKey, Listener

from app.logger import Logger
from ctx.player import PlayerStateManager, Player
from domain.battle import BattleListStateManager
from domain.cast import Cast
from domain.game.control import Key
from domain.game.game import Game
from util.task import Task, StoppableThread, RepeatableTask


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


class AttackTypes:
    SPELL = AttackSpell
    RUNE = AttackRune

    @staticmethod
    def from_str(attack_type: str) -> Cast:
        return AttackTypes.__dict__[attack_type.upper()]


@attr.s
class ComboCaster(RepeatableTask):
    game = attr.ib(type=Game)
    psm = attr.ib(type=PlayerStateManager)
    blsm = attr.ib(type=BattleListStateManager)
    cast_list = attr.ib(type=List[Cast])
    delay = attr.ib(type=float, kw_only=True, default=0.1)
    is_stopped = attr.ib(type=bool, kw_only=True, default=True)
    action_delay = attr.ib(type=float, kw_only=True, default=0)

    def __attrs_post_init__(self):
        self.game.add_task(self)

    def _skip_condition(self) -> bool:
        player: Player = self.psm.get().value
        return not self.game.is_connected() or not player

    def _action(self):
        for cast in cycle(self.cast_list):
            if self.is_stopped:
                break
            player: Player = self.psm.get().value
            battle_state = self.blsm.get()
            if battle_state.is_empty() or len(battle_state.get()) == 0:
                break
            if cast.should_cast(player):
                controller = self.game.controller
                controller.press(cast.key)
            if cast.delay:
                time.sleep(cast.delay)
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
        Logger.log("stopping combo listener")
        if self._listener:
            self._listener.stop()

    def _on_release(self, key: PPKey):
        if key == self.key.pynput_key:
            self.combo_caster.switch()
            off_on = "off" if self.combo_caster.is_stopped else "on"
            Logger.log("combo turn " + off_on)
