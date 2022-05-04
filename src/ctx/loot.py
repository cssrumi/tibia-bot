import time
from typing import List

import attr
from pywinauto import Application

from ctx.player import PlayerStateManager
from ctx.window import WindowStateManager, GameBox, GameWindow
from domain.game.game import Game
from domain.task import Task, StoppableThread


@attr.s
class AutoLootTask(Task):
    game = attr.ib(type=Game)
    psm = attr.ib(type=PlayerStateManager)
    wsm = attr.ib(type=WindowStateManager)
    loot_button = attr.ib(type=str)
    app = attr.ib(init=False, type=Application)
    delay = attr.ib(kw_only=True, type=float, default=60)
    loot_cooldown = attr.ib(kw_only=True, type=float, default=0.2)
    _loot_boxes = attr.ib(init=False, type=List[GameBox], factory=list)

    def __attrs_post_init__(self):
        self.app = self.game.app
        self.game.add_task(self)

    def _run(self):
        self.thread = StoppableThread(target=self._exchange, args=(), daemon=True)
        self.thread.start()

    def _exchange(self):
        while not self.thread.stopped():
            state = self.wsm.get()
            if not self.game.is_connected() or state.is_empty():
                time.sleep(1)
                continue
            player_state = self.psm.get()
            if player_state.is_empty() or not player_state.value.is_healthy():
                time.sleep(1)
                continue
            if not self._loot_boxes:
                self.find_loot_boxes()
            for loot_box in self._loot_boxes:
                self.game.controller.click(self.loot_button, loot_box.center)
                print(loot_box.center)
                time.sleep(self.loot_cooldown)
            print("Loot invoked!")
            time.sleep(self.delay)

    def find_loot_boxes(self):
        window_state = self.wsm.get()
        game_window = GameWindow.from_window_state(window_state)
        print(game_window)
        player_box = game_window.player_box()
        print(player_box)
        b1 = player_box.up()
        b2 = b1.right()
        b3 = b2.down()
        b4 = b3.down()
        b5 = b4.left()
        b6 = b5.left()
        b7 = b6.up()
        b8 = b7.up()
        self._loot_boxes = [b1, b2, b3, b4, b5, b6, b7, b8]
