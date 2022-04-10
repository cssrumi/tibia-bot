from enum import Enum, auto

import win32api
import win32con
import win32gui


class MouseButton(Enum):
    RIGHT = auto()
    LEFT = auto()


def control_click(x, y, handle, button: MouseButton = MouseButton.RIGHT):
    l_param = win32api.MAKELONG(x, y)

    if button == MouseButton.LEFT:
        win32gui.PostMessage(handle, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, l_param)
        win32gui.PostMessage(handle, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, l_param)

    elif button == MouseButton.RIGHT:
        win32gui.PostMessage(handle, win32con.WM_RBUTTONDOWN, 0, l_param)
        win32gui.PostMessage(handle, win32con.WM_RBUTTONUP, 0, l_param)
