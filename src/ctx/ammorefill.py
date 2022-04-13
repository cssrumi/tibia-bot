import time

import attr
import numpy
from pywinauto import Application

from ctx.player import PlayerStateManager
from ctx.window import WindowStateManagerTask
from domain.game.game import Game
from domain.game.locate import locate_image, Position, load_image
from domain.task import Task, StoppableThread

MARGIN = Position(0, 20)

ITEM_POSITION = Position(30, 30)


@attr.s
class AmmoRefillTask(Task):
    game = attr.ib(type=Game)
    psm = attr.ib(type=PlayerStateManager)
    wsm = attr.ib(type=WindowStateManagerTask)
    app = attr.ib(init=False, type=Application)
    quiver = attr.ib(kw_only=True, type=str)
    backpack = attr.ib(kw_only=True, type=str)
    _quiver_img = attr.ib(init=False, type=numpy.ndarray)
    _backpack_img = attr.ib(init=False, type=numpy.ndarray)
    delay = attr.ib(kw_only=True, type=float, default=5)

    def __attrs_post_init__(self):
        self._quiver_img = load_image(self.quiver)
        self._backpack_img = load_image(self.backpack)
        self.app = self.game.app
        self.game.add_task(self)

    def _run(self):
        self.thread = StoppableThread(target=self._refill, args=(), daemon=True)
        self.thread.start()

    def _refill(self):
        while not self.thread.stopped():
            state = self.wsm.get()
            if not self.game.is_connected() or state.is_empty():
                time.sleep(1)
                continue
            player_state = self.psm.get()
            if player_state.is_empty() or not player_state.value.is_healthy():
                time.sleep(1)
                continue
            quiver_pos = locate_image(state, self._quiver_img, precision=0.92)
            backpack_pos = locate_image(state, self._backpack_img, precision=0.92)
            if not quiver_pos.is_empty() and not backpack_pos.is_empty():
                click_pos = backpack_pos.plus(ITEM_POSITION).minus(MARGIN)
                release_pos = quiver_pos.plus(ITEM_POSITION).minus(MARGIN)
                self.game.controller.drag_mouse(click_pos, release_pos)
                print("Ammo refilled!")
                time.sleep(self.delay)
