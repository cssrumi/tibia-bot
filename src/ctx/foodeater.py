import attr

from domain.game.control import Key
from domain.game.game import Game
from util.task import RepeatableTask


@attr.s
class FoodEaterTask(RepeatableTask):
    game = attr.ib(type=Game)
    key = attr.ib(type=Key, kw_only=True)
    action_delay = attr.ib(type=float, kw_only=True, default=30)

    def __attrs_post_init__(self):
        self.game.add_task(self)

    def _skip_condition(self) -> bool:
        return not self.game.is_connected()

    def _action(self):
        self.game.controller.press(self.key)
