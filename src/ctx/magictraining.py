import attr

from ctx.player import PlayerStateManager
from domain.game.control import Key
from domain.game.game import Game
from util.task import RepeatableTask


@attr.s
class MagicTrainingTask(RepeatableTask):
    game = attr.ib(type=Game)
    psm = attr.ib(type=PlayerStateManager)
    key = attr.ib(type=Key, kw_only=True)
    min_mana = attr.ib(kw_only=True, type=int)
    min_health = attr.ib(kw_only=True, type=int, default=100)
    condition_delay = attr.ib(type=float, kw_only=True, default=0.5)

    def __attrs_post_init__(self):
        self.game.add_task(self)

    def _skip_condition(self) -> bool:
        player = self.psm.get().value
        if not self.game.is_connected() or not player:
            return True
        if player.mana >= self.min_mana and player.health >= self.min_health:
            return False
        return True

    def _action(self):
        controller = self.game.controller
        controller.press(self.key)
