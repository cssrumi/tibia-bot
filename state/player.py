import attr
import cv2
import numpy
import numpy as np
from PIL.Image import Image

from game.status import StatusLocation, StatusColor, DEFAULT_STATUS_COLOR
from state.state import StateManager, State


@attr.s(slots=True, frozen=True)
class Player:
    mana = attr.ib(default=None, init=True, type=int)
    health = attr.ib(default=None, init=True, type=int)


@attr.s
class PlayerStateManager(StateManager[Player]):
    status_location = attr.ib(type=StatusLocation, init=False, default=None)
    status_color = attr.ib(type=StatusColor, default=DEFAULT_STATUS_COLOR, kw_only=True)

    def window_listener(self, image: State[Image]):
        if not self.status_location:
            self.status_location = StatusLocation.find(image)
        new_player = self.create_new_player(image)
        self.update(new_player)

    def create_new_player(self, image: State[Image]) -> Player:
        value = cv2.cvtColor(numpy.array(image.value), cv2.COLOR_RGB2BGR)

        mx = self.status_location.mana_status_pos.x
        my = self.status_location.mana_status_pos.y
        mana_status = value[my:my + 1, mx:mx + StatusLocation.status_range]
        mana_status_pc = int(np.count_nonzero(mana_status == self.status_color.mana_color) / 2.7)

        hx = self.status_location.health_status_pos.x
        hy = self.status_location.health_status_pos.y
        health_status = value[hy:hy + 1, hx:hx + StatusLocation.status_range]
        health_status_pc = int(np.count_nonzero(health_status == self.status_color.health_color) / 2.7)

        return Player(mana_status_pc, health_status_pc)
