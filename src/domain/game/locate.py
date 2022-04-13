from threading import Lock
from typing import Tuple

import attr
import cv2
import numpy
import numpy as np
from PIL.Image import Image

from domain.state import State

lock = Lock()


@attr.s(frozen=True, hash=True, eq=True)
class Position:
    __empty = None
    x = attr.ib(type=int, converter=int)
    y = attr.ib(type=int, converter=int)

    def add(self, other: 'Position'):
        return Position(self.x + other.x, self.y + other.y)

    def minus(self, other: 'Position'):
        return Position(self.x - other.x, self.y - other.y)

    def tuple(self) -> Tuple[int, int]:
        return self.x, self.y

    def is_empty(self):
        return self == Position.empty()

    @staticmethod
    def empty() -> 'Position':
        with lock:
            if not Position.__empty:
                Position.__empty = Position(0, 0)
        return Position.__empty


def locate_image(window_state: State[Image], image, precision=0.8, start=True) -> Position:
    if window_state.is_empty():
        print("window state was empty")
        return Position.empty()
    img_rgb = np.array(window_state.value)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = load_image(image)

    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, located_precision, min_loc, position = cv2.minMaxLoc(res)
    if located_precision > precision:
        if start:
            return Position(position[0], position[1])
        else:
            shape = template.shape
            return Position(position[0] + shape[0], position[1] + shape[1])
    return Position.empty()


def load_image(image) -> numpy.ndarray:
    if isinstance(image, numpy.ndarray):
        return image
    if isinstance(image, str):
        return cv2.imread(image, 0)
    raise RuntimeError("Unable to load image of type:" + type(image))


def image_center(image: str) -> Position:
    template = cv2.imread(image, 0)
    width, height = template.shape
    return Position(width / 2, height / 2)
