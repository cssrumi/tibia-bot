import datetime
from typing import List

import attr

from ctx.player import PlayerStateManager, Player
from domain.cast import Cast, Caster
from domain.game.game import Game
from domain.task import Task


@attr.s
class Spell(Cast):

    def should_cast(self, player: Player):
        return player.health <= self.min_health and player.mana >= self.min_mana


@attr.s
class TimedSpell(Cast):
    cooldown = attr.ib(type=float, default=0.0)
    last_usage = attr.ib(type=float, default=0.0, kw_only=True)

    def should_cast(self, player: Player):
        should = self._should_cast(player)
        if not should:
            return False
        if self.cooldown:
            now_in_millis = datetime.datetime.now().microsecond / 1000
            should = now_in_millis > self.last_usage + self.cooldown * 1000
            if should:
                self.last_usage = now_in_millis
            return should
        return True

    def _should_cast(self, player: Player):
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
