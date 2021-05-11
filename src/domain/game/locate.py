from threading import Lock
from typing import Tuple

import attr
import cv2
import numpy as np
from PIL.Image import Image

from domain.state import State

lock = Lock()


@attr.s(frozen=True, hash=True, eq=True)
class Position:
    __empty = None
    x = attr.ib(init=True, type=int, converter=int)
    y = attr.ib(init=True, type=int, converter=int)

    def add(self, other: 'Position'):
        return Position(self.x + other.x, self.y + other.y)

    def minus(self, other: 'Position'):
        return Position(self.x - other.x, self.y - other.y)

    def tuple(self) -> Tuple[int, int]:
        return self.x, self.y

    def is_empty(self):
        return True if self == Position.empty() else False

    @staticmethod
    def empty() -> 'Position':
        with lock:
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


def image_center(image: str) -> Position:
    template = cv2.imread(image, 0)
    width, height = template.shape
    return Position(width / 2, height / 2)
