import time
from functools import wraps
from multiprocessing import Lock
from typing import Callable

import attr
import cv2
import numpy
import pynput
from PIL.Image import Image
from pynput.keyboard import Controller

from ctx.player import PlayerStateManager, Player
from domain.game.game import Game
from domain.game.locate import Position, locate_image
from domain.listener import Listener
from domain.state import StateManager, State, T
from domain.task import Task, StoppableThread

Equipped = bool
STONE_SKIN_ON_IMAGE = '../image/stoneskinon.png'
STONE_SKIN_OFF_IMAGE = '../image/stoneskinoff.png'


@attr.s(slots=True)
class StoneSkinLocation:
    position = attr.ib(type=Position)
    width = attr.ib(type=int)
    height = attr.ib(type=int)

    @staticmethod
    def find(window_state: State[Image]):
        position = locate_image(window_state, STONE_SKIN_OFF_IMAGE, precision=0.99)
        img = cv2.imread(STONE_SKIN_OFF_IMAGE)
        if position.is_empty():
            position = locate_image(window_state, STONE_SKIN_ON_IMAGE, precision=0.99)
            img = cv2.imread(STONE_SKIN_OFF_IMAGE)
        if position.is_empty():
            raise RuntimeError("Unable to find stone skin location.")
        height, width, _ = img.shape
        return StoneSkinLocation(position, width, height)


@attr.s
class StoneSkinStateManager(StateManager[Equipped]):
    stone_skin_location = attr.ib(type=StoneSkinLocation, init=False, default=None)
    verifier = attr.ib(factory=lambda: cv2.imread(STONE_SKIN_ON_IMAGE), init=False, kw_only=True)
    is_processing = attr.ib(init=False, kw_only=False, default=False)

    class Decorator:
        def process(func: Callable):
            def wrapper(self, *args, **kwargs):
                self.is_processing = True
                rv = func(self, *args, **kwargs)
                self.is_processing = False
                return rv
            return wrapper

    def get(self) -> State[Equipped]:
        return super().get()

    @Decorator.process
    def init_stone_skin_location(self, state: State[Image]):
        if state.is_empty():
            return
        self.stone_skin_location = StoneSkinLocation.find(state)

    @Decorator.process
    def check_state(self, state: State[Image]) -> Equipped:
        image = cv2.cvtColor(numpy.array(state.value), cv2.COLOR_RGB2BGR)
        ssx = self.stone_skin_location.position.x
        ssy = self.stone_skin_location.position.y
        dx = self.stone_skin_location.width
        dy = self.stone_skin_location.height

        to_check = image[ssy:ssy+dy, ssx:ssx+dx]
        return cv2.matchTemplate(to_check, self.verifier, cv2.TM_CCOEFF_NORMED) == 1

    def is_equipped(self):
        return self.get().value


@attr.s
class StoneSkinInvoker:
    game = attr.ib(type=Game)
    psm = attr.ib(type=PlayerStateManager)
    key = attr.ib(init=True, type=pynput.keyboard.Key, kw_only=True)
    equip_at = attr.ib(type=int)
    keyboard = attr.ib(default=Controller(), type=Controller, init=False, kw_only=True)
    delay = attr.ib(type=float, default=0.2, kw_only=True)

    def invoke(self, is_equipped: bool):
        player: Player = self.psm.get().value
        if not self.game.is_active() or not player:
            return
        if player.health < self.equip_at and not is_equipped:
            self.keyboard.press(self.key)
            self.keyboard.release(self.key)
            time.sleep(self.delay)


@attr.s
class StoneSkinListener(Listener[Image]):
    sssm = attr.ib(type=StoneSkinStateManager)
    ssi = attr.ib(type=StoneSkinInvoker)

    def update_listener(self, state: State[Image]) -> None:
        if not self.sssm.stone_skin_location:
            self.sssm.init_stone_skin_location(state)
        if self.sssm.is_processing:
            return
        equipped = self.sssm.check_state(state)
        self.sssm.update(equipped)
        self.ssi.invoke(equipped)

