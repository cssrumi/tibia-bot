import random

import attr


@attr.s
class Randomization:
    enabled = attr.ib(type=bool)
    max = attr.ib(type=float, default=0.2)
    min = attr.ib(type=float, default=0)

    @classmethod
    def disabled(cls) -> 'Randomization':
        return cls(False, 0)

    def randomize(self) -> float:
        if not self.enabled:
            return 0
        return random.uniform(self.min, self.max)


@attr.s
class PlayerBasedRandomization(Randomization):
    psm = attr.ib(kw_only=True)
    hp_gate = attr.ib(type=int, kw_only=True, default=50)
    mp_gate = attr.ib(type=int, kw_only=True, default=0)

    def randomize(self) -> float:
        if not self.enabled:
            return 0
        return random.uniform(self.min, self.max) if self.is_player_safe() else 0

    def is_player_safe(self) -> bool:
        state = self.psm.get()
        if state is None or state.is_empty():
            return True
        player = state.get()
        return player is not None and player.health >= self.hp_gate and player.mana >= self.mp_gate
