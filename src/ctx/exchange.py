import time

import attr
import numpy
from pywinauto import Application

from ctx.player import PlayerStateManager
from ctx.window import WindowStateManagerTask
from domain.game.game import Game
from domain.game.locate import locate_image, Position, image_center, load_image
from domain.task import Task, StoppableThread

GP_IMAGE = '../image/100gp.png'
MARGIN = Position(0, 20)


@attr.s
class ExchangeTask(Task):
    game = attr.ib(type=Game)
    psm = attr.ib(type=PlayerStateManager)
    wsm = attr.ib(type=WindowStateManagerTask)
    app = attr.ib(init=False, type=Application)
    exchange_img_path = attr.ib(kw_only=True, type=str, default=GP_IMAGE)
    exchange_img_center = attr.ib(init=False, type=Position)
    _exchange_img = attr.ib(init=False, type=numpy.ndarray)
    delay = attr.ib(kw_only=True, type=float, default=0.5)

    def __attrs_post_init__(self):
        self.exchange_img_center = image_center(self.exchange_img_path)
        self._exchange_img = load_image(self.exchange_img_path)
        self.app = self.game.app
        self.game.add_task(self)

    def _run(self):
        self.thread = StoppableThread(target=self._exchange, args=(), daemon=True)
        self.thread.start()

    def _exchange(self):
        while not self.thread.stopped():
            state = self.wsm.get()
            if not self.game.is_active() or state.is_empty() or not self.game.is_connected():
                time.sleep(1)
                continue
            player_state = self.psm.get()
            if player_state.is_empty() or not player_state.value.is_healthy():
                time.sleep(1)
                continue
            cash = locate_image(state, self._exchange_img, precision=0.92)
            if not cash.is_empty():
                pos_to_click = cash.add(self.exchange_img_center).minus(MARGIN)
                self.app.window().click(button='right', coords=pos_to_click.tuple())
                time.sleep(self.delay)
                print("Cash exchanged!")
