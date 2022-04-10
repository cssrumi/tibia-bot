from typing import List

import attr
from pynput.keyboard import Controller

from domain.cast import Cast, Caster
from ctx.player import PlayerStateManager, Player
from domain.game.game import Game
from domain.task import Task


@attr.s
class Spell(Cast):

    def should_cast(self, player: Player):
        return player.health <= self.min_health and player.mana >= self.min_mana


@attr.s
class Potion(Cast):
    min_mana = attr.ib(type=int, kw_only=True, default=100)
    min_health = attr.ib(type=int, kw_only=True, default=100)

    def should_cast(self, player: Player):
        return player.health <= self.min_health and player.mana <= self.min_mana


@attr.s
class HealerTask(Task):
    game = attr.ib(type=Game)
    psm = attr.ib(type=PlayerStateManager)
    spells = attr.ib(type=List[Spell])
    potions = attr.ib(type=List[Potion])
    controller = attr.ib(type=Controller, factory=Controller, kw_only=True)
    _spell_caster = attr.ib(type=Caster, init=False)
    _potion_caster = attr.ib(type=Caster, init=False)

    def __attrs_post_init__(self):
        self._spell_caster = Caster(self.game, self.psm, self.spells)
        self._potion_caster = Caster(self.game, self.psm, self.potions)
        self.game.add_task(self)

    def _run(self):
        self._spell_caster.start()
        self._potion_caster.start()

    def is_started(self):
        return self._spell_caster.is_started() and self._potion_caster.is_started()

    def stop(self):
        self._spell_caster.stop()
        self._potion_caster.stop()
