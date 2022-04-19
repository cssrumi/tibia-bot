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


#FIRST_SLOT=45X52


@attr.s
class RefillTask(Task):
    game = attr.ib(type=Game)
    psm = attr.ib(type=PlayerStateManager)
    wsm = attr.ib(type=WindowStateManagerTask)
    app = attr.ib(init=False, type=Application)
    from_container = attr.ib(kw_only=True, type=str)
    to_container = attr.ib(kw_only=True, type=str)
    _from_container_img = attr.ib(init=False, type=numpy.ndarray)
    _to_container_img = attr.ib(init=False, type=numpy.ndarray)
    delay = attr.ib(kw_only=True, type=float, default=15)

    def __attrs_post_init__(self):
        self._from_container_img = load_image(self.from_container)
        self._to_container_img = load_image(self.to_container)
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
            from_container_pos = locate_image(state, self._from_container_img, precision=0.92)
            to_container_pos = locate_image(state, self._to_container_img, precision=0.92)
            if not to_container_pos.is_empty() and not from_container_pos.is_empty():
                click_pos = from_container_pos.plus(ITEM_POSITION).minus(MARGIN)
                release_pos = to_container_pos.plus(ITEM_POSITION).minus(MARGIN)
                self.game.controller.drag_mouse(click_pos, release_pos)
                print("item refilled!")
                time.sleep(self.delay)
