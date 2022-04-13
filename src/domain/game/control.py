import attr
import win32api
import win32con
import win32gui
from pynput.keyboard import Controller as PPController
from pynput.keyboard import Key as PPKey
from pywinauto import WindowSpecification

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


MouseButton = str


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
    hwnd = attr.ib(type=int, init=False)

    def __attrs_post_init__(self):
        self.window = self.game.app.window()
        self.hwnd = win32gui.FindWindow(None, self.game.name)

    def click(self, button: MouseButton, pos_to_click: Position):
        self.window.click(button=button, coords=pos_to_click.tuple())

    def drag_mouse(self, press_pos: Position, release_pos: Position):
        press_lParam = self.pos_to_lParam(press_pos)
        release_lParam = self.pos_to_lParam(release_pos)
        win32gui.PostMessage(self.hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, press_lParam)
        win32gui.PostMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, press_lParam)
        win32gui.PostMessage(self.hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, release_lParam)
        win32gui.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, None, release_lParam)

    def pos_to_lParam(self, pos: Position):
        return win32api.MAKELONG(pos.x, pos.y)

    def press(self, key: Key):
        raise NotImplementedError()


@attr.s
class PywinautoController(Controller):

    def press(self, key: Key):
        self.window.send_keystrokes(key.pywinauto_key)


@attr.s
class PynputController(Controller):
    keyboard = attr.ib(default=PPController(), type=PPController, init=False, kw_only=True)

    def press(self, key: Key):
        self.keyboard.press(key.pynput_key)
        self.keyboard.release(key.pynput_key)


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


def create_controller(game: 'Game') -> Controller:
    # return ControllerFacade(game)
    # return PynputController(game)
    return PywinautoController(game)
