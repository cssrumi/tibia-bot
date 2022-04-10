import attr
import win32api
import win32con
import win32gui
from pywinauto import WindowSpecification
from pynput.keyboard import Key as PPKey

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
    CAPS_LOCK = Key('{CAPSLOCK}', PPKey.caps_lock)
    SPACE = Key('{SPACE}', PPKey.space)


class MouseButtons:
    RIGHT = 'right'
    LEFT = 'left'


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

    def __attrs_post_init__(self):
        self.window = self.game.app.window()

    def click(self, button: MouseButtons, pos_to_click: Position):
        self.window.click(button=button, coords=pos_to_click.tuple())

    def press(self, key: Key):
        self.window.send_keystrokes(key.pywinauto_key)
