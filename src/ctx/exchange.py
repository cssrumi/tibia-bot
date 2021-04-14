import time

import attr
import win32api
import win32con
import win32gui
from pywinauto import Application

from ctx.player import PlayerStateManager
from ctx.window import Window
from game.game import Game
from game.locate import locate_image, Position, image_center
from task import Task, StoppableThread


GP_IMAGE = '../image/100gp.png'
MARGIN = Position(0, 20)


@attr.s
class ExchangeTask(Task):
    game = attr.ib(type=Game)
    psm = attr.ib(type=PlayerStateManager)
    wsm = attr.ib(type=Window)
    app = attr.ib(kw_only=True, type=Application, factory=Application)
    exchange_img = attr.ib(kw_only=True, type=str, default=GP_IMAGE)
    exchange_img_center = attr.ib(init=False, type=Position)
    delay = attr.ib(kw_only=True, type=float, default=0.5)
    _is_connected = attr.ib(init=False, type=bool, default=False)

    def __attrs_post_init__(self):
        self.exchange_img_center = image_center(self.exchange_img)

    def _run(self):
        self.thread = StoppableThread(target=self._exchange, args=(), daemon=True)
        self.thread.start()

    def _connect(self) -> bool:
        if self._is_connected or not self.game.is_active():
            return False
        self.app.connect(title=self.game.name)
        self._is_connected = True
        print('exchange application connected')
        return True

    def _exchange(self):
        while not self.thread.stopped():
            state = self.wsm.get()
            if not self.game.is_active() or state.is_empty():
                time.sleep(1)
                continue
            if not self._is_connected:
                self._connect()
                time.sleep(1)
                continue
            player_state = self.psm.get()
            if player_state.is_empty() or not player_state.value.is_healthy():
                time.sleep(1)
                continue
            cash = locate_image(state, self.exchange_img)
            if cash is not Position.empty():
                pos_to_click = cash.add(self.exchange_img_center).minus(MARGIN)
                self.app.window().click(button='right', coords=pos_to_click.tuple())
                time.sleep(self.delay)
                print("Cash exchanged!")


def control_click(x, y, handle, button='right'):
    print(handle)

    l_param = win32api.MAKELONG(x, y)

    if button == 'left':
        win32gui.PostMessage(handle, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, l_param)
        win32gui.PostMessage(handle, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, l_param)

    elif button == 'right':
        win32gui.PostMessage(handle, win32con.WM_RBUTTONDOWN, 0, l_param)
        win32gui.PostMessage(handle, win32con.WM_RBUTTONUP, 0, l_param)
