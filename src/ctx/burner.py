import atexit
import os
import time
from threading import Lock

import attr
import pynput
import win32api
import win32con
import win32gui

from domain.game.game import Game
from domain.task import Task, StoppableThread

lock = Lock()

FUNCTION_KEYS = {
    'f1': 0x70,
    'f2': 0x71,
    'f3': 0x72,
    'f4': 0x73,
    'f5': 0x74,
    'f6': 0x75,
    'f7': 0x76,
    'f8': 0x77,
    'f9': 0x78,
    'f10': 0x79,
    'f11': 0x7A,
    'f12': 0x7B,
}


class WindowsInhibitor:
    __inhibited = False
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001

    @staticmethod
    def inhibit():
        if os.name != 'nt':
            print(f"Unhandled os type: {os.name}")
            return
        with lock:
            if WindowsInhibitor.__inhibited:
                return
            import ctypes
            print("Preventing Windows from going to sleep")
            ctypes.windll.kernel32.SetThreadExecutionState(
                WindowsInhibitor.ES_CONTINUOUS |
                WindowsInhibitor.ES_SYSTEM_REQUIRED
            )
            atexit.register(WindowsInhibitor.uninhibit)
            WindowsInhibitor.__inhibited = True

    @staticmethod
    def uninhibit():
        if os.name != 'nt':
            print(f"Unhandled os type: {os.name}")
            return
        import ctypes
        print("Allowing Windows to go to sleep")
        ctypes.windll.kernel32.SetThreadExecutionState(
            WindowsInhibitor.ES_CONTINUOUS
        )


@attr.s
class ShadowBurner(Task):
    game = attr.ib(type=Game)
    food_key = attr.ib(type=pynput.keyboard.Key, kw_only=True)
    mana_burn_key = attr.ib(type=pynput.keyboard.Key, kw_only=True)
    delay = attr.ib(init=False, kw_only=True, type=float, default=1.05)
    hwnd = attr.ib(init=False, kw_only=False)

    def _run(self):
        if not self._connect():
            return
        self.thread = StoppableThread(target=self._burn, args=(), daemon=True)
        self.thread.start()
        WindowsInhibitor.inhibit()

    def _connect(self) -> bool:
        try:
            self.hwnd = win32gui.FindWindow(None, self.game.name)
            print(f'ShadowBurner connected with {self.game.name} {self.hwnd}')
            return True
        except RuntimeError as e:
            print(f'Unable to connect ShadowBurner to {self.game.name}. Reason: {e}')
            return False

    def _burn(self):
        while not self.thread.stopped():
            self._press_and_release(self.food_key)
            self._press_and_release(self.mana_burn_key)
            time.sleep(self.delay)

    def _press_and_release(self, key: pynput.keyboard.Key):
        k = FUNCTION_KEYS.get(key.name) if isinstance(key, pynput.keyboard.Key) else ord(key)
        win32api.PostMessage(self.hwnd, win32con.WM_KEYDOWN, k, 0)
        # win32api.PostMessage(self.hwnd, win32con.WM_KEYUP, k, 0)
