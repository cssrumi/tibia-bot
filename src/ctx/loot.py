import time
from enum import Enum
from typing import List

import attr
from pynput.keyboard import Key as PPKey, Listener
from pywinauto import Application

from app.logger import Logger, LogLevel
from ctx.player import PlayerStateManager
from ctx.window import WindowStateManager, GameBox, GameWindow
from domain.game.control import Key
from domain.game.game import Game
from util.switch import Switchable
from util.task import RepeatableTask, Task, StoppableThread


@attr.s
class LootAction:
    game = attr.ib(type=Game)
    wsm = attr.ib(type=WindowStateManager)
    loot_button = attr.ib(type=str)
    app = attr.ib(init=False, type=Application)
    loot_cooldown = attr.ib(kw_only=True, type=float, default=0.2)
    _loot_boxes = attr.ib(init=False, type=List[GameBox], factory=list)

    def find_loot_boxes(self):
        window_state = self.wsm.get()
        game_window = GameWindow.from_window_state(window_state)
        Logger.log(game_window, lvl=LogLevel.DEBUG)
        player_box = game_window.player_box()
        Logger.log(player_box, lvl=LogLevel.DEBUG)
        b1 = player_box.up()
        b2 = b1.right()
        b3 = b2.down()
        b4 = b3.down()
        b5 = b4.left()
        b6 = b5.left()
        b7 = b6.up()
        b8 = b7.up()
        self._loot_boxes = [b1, b2, b3, b4, b5, b6, b7, b8]

    def invoke(self):
        if not self._loot_boxes:
            self.find_loot_boxes()
        for loot_box in self._loot_boxes:
            self.game.controller.click(self.loot_button, loot_box.center)
            Logger.log(loot_box.center, lvl=LogLevel.DEBUG)
            time.sleep(self.loot_cooldown)


@attr.s
class LootListener(Task, Switchable):
    invoker = attr.ib(type=LootAction)
    key = attr.ib(type=Key)
    _listener = attr.ib(init=False, type=Listener)

    def __attrs_post_init__(self):
        self.invoker.game.add_task(self)

    def _run(self):
        self.thread = StoppableThread(target=self._listen, args=(), daemon=True)
        self.thread.start()

    def _listen(self):
        self.invoker.game.register_on_exit(self._stop_listener)
        with Listener(on_release=self._on_release) as listener:
            self._listener = listener
            listener.join()

    def _stop_listener(self):
        Logger.log("stopping loot listener")
        if self._listener:
            self._listener.stop()

    def _on_release(self, key: PPKey):
        if self.is_stopped or key != self.key.pynput_key or not self.invoker.game.is_active():
            return
        self.invoker.invoke()


class LootType(Enum):
    REPEATABLE = 0
    ON_KEY = 1

    @staticmethod
    def from_str(loot_type: str) -> Key:
        return LootType[loot_type.upper()]


@attr.s
class AutoLootTask(RepeatableTask):
    game = attr.ib(type=Game)
    psm = attr.ib(type=PlayerStateManager)
    wsm = attr.ib(type=WindowStateManager)
    invoker = attr.ib(type=LootAction)
    action_delay = attr.ib(type=float, kw_only=True, default=10)

    def __attrs_post_init__(self):
        self.game.add_task(self)

    def _skip_condition(self) -> bool:
        state = self.wsm.get()
        if not self.game.is_connected() or state.is_empty():
            return True
        player_state = self.psm.get()
        if player_state.is_empty() or not player_state.value.is_healthy():
            return True
        return False

    def _action(self):
        self.invoker.invoke()
