from enum import Enum

import attr

from domain.game.locate import load_image, Position


class Monster(Enum):
    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, image_loc):
        self._image_loc = image_loc
        self._image = None

    def image(self):
        if not self._image and self._image_loc:
            self._image = load_image(self._image_loc)
        return self._image

    UNKNOWN = None
    NECROMANCER = "../image/monsters/necromancer.png"


@attr.s
class DetectedMonster:
    position = attr.ib(type=Position)
    monster = attr.ib(type=Monster)
    is_targeted = attr.ib(type=bool)
