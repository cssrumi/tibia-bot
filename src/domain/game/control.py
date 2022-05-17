import re
import time
from threading import Lock

import attr
import win32api
import win32con
import win32gui
from pynput.keyboard import Controller as PPController
from pynput.keyboard import Key as PPKey
from pywinauto import WindowSpecification

from app.logger import Logger
from domain.game.locate import Position


@attr.s
class Key:
    pywinauto_key = attr.ib(type=str)
    pynput_key = attr.ib(type=PPKey)


class Keys:
    F1 = Key('{F1}', PPKey.f1)
    F2 = Key('{F2}', PPKey.f2)
    F3 = Key('{F3}', PPKey.f3)
    F4 = Key('{F4}', PPKey.f4)
    F5 = Key('{F5}', PPKey.f5)
    F6 = Key('{F6}', PPKey.f6)
    F7 = Key('{F7}', PPKey.f7)
    F8 = Key('{F8}', PPKey.f8)
    F9 = Key('{F9}', PPKey.f9)
    F10 = Key('{F10}', PPKey.f10)
    F11 = Key('{F11}', PPKey.f11)
    F12 = Key('{F12}', PPKey.f12)
    N1 = Key('{1}', '1')
    N2 = Key('{2}', '2')
    N3 = Key('{3}', '3')
    N4 = Key('{4}', '4')
    CAPS_LOCK = Key('{CAPSLOCK}', PPKey.caps_lock)
    SPACE = Key('{SPACE}', PPKey.space)
    ENTER = Key('{ENTER}', PPKey.enter)

    @staticmethod
    def from_str(key: str) -> Key:
        return Keys.__dict__[key.upper()]


MouseButton = str


class MouseButtons:
    RIGHT = 'right'
    LEFT = 'left'

    @staticmethod
    def from_str(value: str) -> MouseButton:
        return MouseButtons.__dict__[value.upper()]


def control_click(x, y, handle, button: MouseButtons = MouseButtons.RIGHT):
    l_param = win32api.MAKELONG(x, y)

    if button == MouseButtons.LEFT:
        win32gui.PostMessage(handle, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, l_param)
        win32gui.PostMessage(handle, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, l_param)

    elif button == MouseButtons.RIGHT:
        win32gui.PostMessage(handle, win32con.WM_RBUTTONDOWN, 0, l_param)
        win32gui.PostMessage(handle, win32con.WM_RBUTTONUP, 0, l_param)


@attr.s
class Controller:
    game = attr.ib(type='Game')
    window = attr.ib(type=WindowSpecification, init=False)
    hwnd = attr.ib(type=int, init=False)
    mouse_lock = attr.ib(init=False, type=Lock, default=Lock())
    mouse_delay = attr.ib(type=float, default=0.2, kw_only=True)

    def __attrs_post_init__(self):
        self.window = self.game.app.window()
        self.hwnd = win32gui.FindWindow(None, self.game.name)

    def click(self, button: MouseButton, pos_to_click: Position):
        with self.mouse_lock:
            self.window.click(button=button, coords=pos_to_click.tuple())
            time.sleep(self.mouse_delay)

    def move(self, pos_to_move: Position):
        with self.mouse_lock:
            move_lParam = self.pos_to_lParam(pos_to_move)
            win32gui.PostMessage(self.hwnd, win32con.WM_MOUSEMOVE, None, move_lParam)
            time.sleep(self.mouse_delay)

    def drag_mouse(self, press_pos: Position, release_pos: Position):
        with self.mouse_lock:
            press_lParam = self.pos_to_lParam(press_pos)
            release_lParam = self.pos_to_lParam(release_pos)
            win32gui.PostMessage(self.hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, press_lParam)
            win32gui.PostMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, press_lParam)
            win32gui.PostMessage(self.hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, release_lParam)
            win32gui.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, None, release_lParam)
            time.sleep(self.mouse_delay)

    def pos_to_lParam(self, pos: Position):
        return win32api.MAKELONG(pos.x, pos.y)

    def press(self, key: Key):
        raise NotImplementedError()

    def write(self, msg: str):
        raise NotImplementedError()


@attr.s
class PywinautoController(Controller):

    def press(self, key: Key):
        self.window.send_keystrokes(key.pywinauto_key)

    def write(self, msg: str):
        if not msg:
            return
        try:
            if not msg.isalnum():
                Logger.warn(f"Non alphanumeric msg: {msg}")
                msg = re.sub(r'[^A-Za-z0-9 ]+', '', msg)
            self.window.send_chars(msg, with_tabs=False, with_newlines=False)
        except RuntimeError as e:
            Logger.error(f"Unable to write: {msg}. Reason: {e}")


@attr.s
class PynputController(Controller):
    keyboard = attr.ib(default=PPController(), type=PPController, init=False, kw_only=True)

    def press(self, key: Key):
        self.keyboard.press(key.pynput_key)
        self.keyboard.release(key.pynput_key)

    def write(self, msg: str):
        # TODO: impl
        Logger.error("Unsupported operation type")


@attr.s
class ControllerFacade(Controller):
    pywinauto = attr.ib(type=PywinautoController, init=False)
    pynput = attr.ib(type=PywinautoController, init=False)

    def __attrs_post_init__(self):
        self.pywinauto = PywinautoController(self.game)
        self.pynput = PynputController(self.game)

    def press(self, key: Key):
        controller = self.pynput if self.game.is_active() else self.pywinauto
        controller.press(key)

    def write(self, msg: str):
        controller = self.pynput if self.game.is_active() else self.pywinauto
        controller.window(msg)


def create_controller(game: 'Game') -> Controller:
    # return ControllerFacade(game)
    # return PynputController(game)
    return PywinautoController(game)
