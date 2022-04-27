from threading import Lock
from typing import Tuple, Generator, Union

import attr
import cv2
import numpy
import numpy as np

lock = Lock()


@attr.s(frozen=True, hash=True, eq=True)
class Position:
    __empty = None
    x = attr.ib(type=int, converter=int)
    y = attr.ib(type=int, converter=int)

    def plus(self, other: 'Position'):
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


def locate_image(origin: numpy.ndarray, image, precision=0.8, start=True, method: int = cv2.TM_CCOEFF_NORMED) -> Position:
    if origin is None:
        print("Origin was empty")
        return Position.empty()
    template = load_image(image)
    res = cv2.matchTemplate(origin, template, method)
    min_val, located_precision, min_loc, position = cv2.minMaxLoc(res)
    if located_precision > precision:
        if start:
            return Position(position[0], position[1])
        else:
            shape = template.shape
            return Position(position[0] + shape[0], position[1] + shape[1])
    return Position.empty()


def locate_image_gen(origin: numpy.ndarray, image, precision=0.8, start=True, method: int = cv2.TM_CCOEFF_NORMED) -> \
Generator[Position, None, None]:
    if origin is None:
        print("Origin was empty")
        yield Position.empty()

    template = load_image(image)
    res = cv2.matchTemplate(origin, template, method)
    positions = np.where(res > precision)
    for position in zip(*positions[::-1]):
        if start:
            yield Position(position[0], position[1])
        else:
            shape = template.shape
            yield Position(position[0] + shape[0], position[1] + shape[1])
    yield


def load_image(image: Union[str, numpy.ndarray], mask: int = 0) -> numpy.ndarray:
    if isinstance(image, numpy.ndarray):
        return image
    if isinstance(image, str):
        return cv2.imread(image, mask)
    raise RuntimeError("Unable to load image of type:" + type(image))


def image_center(image: Union[str, numpy.ndarray]) -> Position:
    template = load_image(image)
    height, width = template.shape
    print(width, height)
    return Position(int(width / 2), int(height / 2))
