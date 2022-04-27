import time

import attr

from domain.battle import BattleListStateManager
from domain.game.control import MouseButtons
from domain.game.game import Game
from domain.game.locate import Position
from domain.task import Task, StoppableThread


MOVE_MOUSE_POS = Position(0, 10)


@attr.s
class AutoTargetTask(Task):
    game = attr.ib(type=Game)
    blsm = attr.ib(type=BattleListStateManager)
    delay = attr.ib(init=False, kw_only=True, type=float, default=1.0)

    def __attrs_post_init__(self):
        self.game.add_task(self)

    def _run(self):
        self.thread = StoppableThread(target=self._auto_attack, args=(), daemon=True)
        self.thread.start()

    def _auto_attack(self):
        while not self.thread.stopped():
            if not self.game.is_connected():
                time.sleep(0.5)
                continue
            state = self.blsm.get()
            if state.is_empty():
                time.sleep(0.5)
                print("Battle state was empty")
                continue
            detected_monsters = state.get()
            is_targeted = any(map(lambda dm: dm.is_targeted, detected_monsters))
            print("is targeted:", is_targeted, ", detected monsters:", len(detected_monsters))
            if not is_targeted and detected_monsters:
                monster = min(detected_monsters, key=lambda dm: dm.position.y)
                controller = self.game.controller
                controller.click(MouseButtons.LEFT, monster.position)
                controller.move(monster.position.plus(MOVE_MOUSE_POS))
                print("monster in pos:", monster.position, "targeted")
            else:
                print("monster already targeted or nothing detected")
            time.sleep(self.delay)
