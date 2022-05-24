import attr

from app.logger import Logger, LogLevel
from domain.battle import BattleListStateManager
from domain.game.control import MouseButtons
from domain.game.game import Game
from domain.game.locate import Position
from util.task import RepeatableTask

MOVE_MOUSE_POS = Position(0, 10)


@attr.s
class AutoTargetTask(RepeatableTask):
    game = attr.ib(type=Game)
    blsm = attr.ib(type=BattleListStateManager)
    action_delay = attr.ib(type=float, kw_only=True, default=1)

    def __attrs_post_init__(self):
        self.game.add_task(self)

    def _skip_condition(self) -> bool:
        return not self.game.is_connected()

    def _action(self):
        state = self.blsm.get()
        if state.is_empty():
            Logger.debug("Battle state was empty")
            return
        detected_monsters = state.get()
        is_targeted = any(map(lambda dm: dm.is_targeted, detected_monsters))
        Logger.debug(f"is targeted: {is_targeted}, detected monsters: {len(detected_monsters)}")
        if not is_targeted and detected_monsters:
            monster = min(detected_monsters, key=lambda dm: dm.position.y)
            controller = self.game.controller
            controller.click(MouseButtons.LEFT, monster.position)
            controller.move(monster.position.plus(MOVE_MOUSE_POS))
            Logger.info(f"monster in pos: {monster.position} targeted")
        else:
            Logger.info("monster already targeted or nothing detected")
