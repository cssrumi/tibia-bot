import attr
import numpy
from pywinauto import Application

from app.logger import Logger
from ctx.player import PlayerStateManager
from ctx.window import WindowStateManager
from domain.game.control import MouseButtons
from domain.game.game import Game
from domain.game.locate import locate_image, Position, image_center, load_image
from util.task import RepeatableTask

GP_IMAGE = '../image/100gp.png'
MARGIN = Position(0, 20)


@attr.s
class ExchangeTask(RepeatableTask):
    game = attr.ib(type=Game)
    psm = attr.ib(type=PlayerStateManager)
    wsm = attr.ib(type=WindowStateManager)
    app = attr.ib(init=False, type=Application)
    exchange_img_path = attr.ib(kw_only=True, type=str, default=GP_IMAGE)
    exchange_img_center = attr.ib(init=False, type=Position)
    _exchange_img = attr.ib(init=False, type=numpy.ndarray)
    action_delay = attr.ib(kw_only=True, type=float, default=0.5)

    def __attrs_post_init__(self):
        self.exchange_img_center = image_center(self.exchange_img_path)
        self._exchange_img = load_image(self.exchange_img_path)
        self.app = self.game.app
        self.game.add_task(self)

    def _skip_condition(self) -> bool:
        if not self.game.is_connected():
            return True
        player_state = self.psm.get()
        if player_state.is_empty() or not player_state.value.is_healthy():
            return True
        return False

    def _action(self):
        state = self.wsm.get()
        if not state or state.is_empty():
            return
        origin = state.get().ndarray()
        cash = locate_image(origin, self._exchange_img, precision=0.92)
        if not cash.is_empty():
            pos_to_click = cash.plus(self.exchange_img_center).minus(MARGIN)
            self.game.controller.click(MouseButtons.RIGHT, pos_to_click)
            Logger.log("Cash exchanged!")
