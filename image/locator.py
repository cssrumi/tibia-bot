import attr
import cv2
import numpy as np
from PIL.Image import Image

from state.state import State


@attr.s(frozen=True, hash=True, eq=True)
class Position:
    __empty = None
    x = attr.ib(init=True, type=int)
    y = attr.ib(init=True, type=int)

    @staticmethod
    def empty() -> 'Position':
        if not Position.__empty:
            Position.__empty = Position(0, 0)
        return Position.__empty


def locate_image(window_state: State[Image], image, precision=0.8):
    if window_state.is_empty():
        print("window state was empty")
        return Position.empty()
    img_rgb = np.array(window_state.value)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(image, 0)

    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, located_precision, min_loc, position = cv2.minMaxLoc(res)
    if located_precision > precision:
        return Position(position[0], position[1])
    return Position.empty()


def find_mana(window_state: State[Image]) -> Position:
    return locate_image(window_state, 'image/mana.png')


def find_health(window_state: State[Image]) -> Position:
    return locate_image(window_state, 'image/health.png')


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
        mana_loc = find_mana(window_state)
        health_loc = find_health(window_state)
        return StatusLocation(mana_loc, health_loc)


@attr.s(slots=True, frozen=True)
class StatusColor:
    mana_color = attr.ib(init=True)
    health_color = attr.ib(init=True)

    @staticmethod
    def find():
        mana = cv2.imread('image/fullmana.png', cv2.COLOR_RGB2BGR)
        mc = mana[6, 2]
        health = cv2.imread('image/fullhealth.png', cv2.COLOR_RGB2BGR)
        hc = health[6, 2]
        return StatusColor(mc, hc)


DEFAULT_STATUS_COLOR = StatusColor.find()
