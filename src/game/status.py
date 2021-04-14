import attr
import cv2
from PIL.Image import Image

from game.locate import Position, locate_image
from state import State

MANA_POSITION_IMAGE = '../image/mana.png'
HEALTH_POSITION_IMAGE = '../image/health.png'
MANA_STATUS_IMAGE = '../image/fullmana.png'
HEALTH_STATUS_IMAGE = '../image/fullhealth.png'


@attr.s(slots=True)
class StatusLocation:
    status_range = 90
    status_x_offset = 16
    status_y_offset = 6
    mana_pos = attr.ib(type=Position, init=True)
    health_pos = attr.ib(type=Position, init=True)
    mana_status_pos = attr.ib(type=Position, default=None)
    health_status_pos = attr.ib(type=Position, default=None)

    def __attrs_post_init__(self):
        mx = self.mana_pos.x + StatusLocation.status_x_offset
        my = self.mana_pos.y + StatusLocation.status_y_offset
        self.mana_status_pos = Position(mx, my)
        hx = self.health_pos.x + StatusLocation.status_x_offset
        hy = self.health_pos.y + StatusLocation.status_y_offset
        self.health_status_pos = Position(hx, hy)

    @staticmethod
    def find(window_state: State[Image]):
        mana_loc = StatusLocation.find_mana(window_state)
        health_loc = StatusLocation.find_health(window_state)
        return StatusLocation(mana_loc, health_loc)

    @staticmethod
    def find_mana(window_state: State[Image]) -> Position:
        return locate_image(window_state, MANA_POSITION_IMAGE)

    @staticmethod
    def find_health(window_state: State[Image]) -> Position:
        return locate_image(window_state, HEALTH_POSITION_IMAGE)


@attr.s(slots=True, frozen=True)
class StatusColor:
    mana_color = attr.ib(init=True)
    health_color = attr.ib(init=True)

    @staticmethod
    def find():
        mana = cv2.imread(MANA_STATUS_IMAGE, cv2.COLOR_RGB2BGR)
        mc = mana[6, 2]
        health = cv2.imread(HEALTH_STATUS_IMAGE, cv2.COLOR_RGB2BGR)
        hc = health[6, 2]
        return StatusColor(mc, hc)


DEFAULT_STATUS_COLOR = StatusColor.find()
