from datetime import datetime
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
from domain.state import StateManager, State

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

        to_check = image[ssy:ssy + dy, ssx:ssx + dx]
        return cv2.matchTemplate(to_check, self.verifier, cv2.TM_CCOEFF_NORMED) == 1

    def is_equipped(self):
        return self.get().value


@attr.s
class StoneSkinInvoker:
    game = attr.ib(type=Game)
    psm = attr.ib(type=PlayerStateManager)
    key = attr.ib(type=pynput.keyboard.Key, kw_only=True)
    equip_at = attr.ib(type=int)
    keyboard = attr.ib(default=Controller(), type=Controller, init=False, kw_only=True)
    delay = attr.ib(default=200, type=int, kw_only=True)
    last_invocation = attr.ib(default=0, type=int, init=False)

    def invoke(self, is_equipped: bool) -> None:
        player: Player = self.psm.get().value
        if not self.game.is_active() or not player:
            return
        now_in_millis = StoneSkinInvoker._now_in_millis()
        if self.last_invocation + self.delay > now_in_millis:
            return
        if player.health < self.equip_at and not is_equipped:
            self.keyboard.press(self.key)
            self.keyboard.release(self.key)
            self.last_invocation = now_in_millis

    @staticmethod
    def _now_in_millis():
        return int(datetime.now().timestamp() * 1000)


@attr.s
class StoneSkinImageListener(Listener[Image]):
    sssm = attr.ib(type=StoneSkinStateManager)

    def update_listener(self, state: State[Image]) -> None:
        if not self.sssm.stone_skin_location:
            self.sssm.init_stone_skin_location(state)
        if self.sssm.is_processing:
            return
        equipped = self.sssm.check_state(state)
        self.sssm.update(equipped)
