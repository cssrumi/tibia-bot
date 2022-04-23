import attr
import cv2
import numpy
import numpy as np

from ctx.window import Window
from domain.game.status import StatusLocation, StatusColor, DEFAULT_STATUS_COLOR
from domain.listener import Listener
from domain.state import StateManager, State


@attr.s(slots=True, frozen=True)
class Player:
    mana = attr.ib(default=None, type=int)
    health = attr.ib(default=None, type=int)

    def is_healthy(self):
        return self.health > 95


@attr.s
class PlayerStateManager(StateManager[Player]):
    status_location = attr.ib(type=StatusLocation, init=False, default=None)
    status_color = attr.ib(type=StatusColor, default=DEFAULT_STATUS_COLOR, kw_only=True)

    def get(self) -> State[Player]:
        return super().get()

    def init_status_location(self, state: State[Window]):
        if state.is_empty():
            return
        self.status_location = StatusLocation.find(state)

    def create_new_player(self, state: State[Window]) -> Player:
        origin = cv2.cvtColor(numpy.array(state.get().image()), cv2.COLOR_RGB2BGR)

        mx = self.status_location.mana_status_pos.x
        my = self.status_location.mana_status_pos.y
        mana_status = origin[my:my + 1, mx:mx + StatusLocation.status_range]
        mana_status_pc = int(np.count_nonzero(mana_status == self.status_color.mana_color) / 2.7)

        hx = self.status_location.health_status_pos.x
        hy = self.status_location.health_status_pos.y
        health_status = origin[hy:hy + 1, hx:hx + StatusLocation.status_range]
        health_status_pc = int(np.count_nonzero(health_status == self.status_color.health_color) / 2.7)

        return Player(mana_status_pc, health_status_pc)


@attr.s
class PlayerImageListener(Listener[Window]):
    psm = attr.ib(type=PlayerStateManager)

    def update_listener(self, state: State[Window]) -> None:
        if not self.psm.status_location:
            self.psm.init_status_location(state)
        if state.is_empty():
            pass
        new_player = self.psm.create_new_player(state)
        self.psm.update(new_player)
