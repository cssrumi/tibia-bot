from typing import Generator, Optional, Type

import numpy

from ctx.window import Window
from domain.game.locate import Position, locate_image, locate_image_gen, load_image
from domain.state import State

containers_path = '../image/containers/'


class Containers:

    @classmethod
    def from_str(cls, container: str) -> str:
        return cls.__dict__[container.upper()]


class Quivers(Containers):
    BLUE = containers_path + 'bluequiver.png'


class Backpacks(Containers):
    BLUE = containers_path + 'bluebackpack.png'
    BEACH = containers_path + 'beachbackpack.png'
    CRYSTAL = containers_path + 'crystalbackpack.png'


class Depots(Containers):
    BOX_XVIII = containers_path + 'depotboxxviii.png'


class ContainerTypes:
    QUIVER = Quivers
    BACKPACK = Backpacks
    DEPOT = Depots

    @staticmethod
    def from_str(c_type: str) -> Containers:
        return ContainerTypes.__dict__[c_type.upper()]


class Container:
    FIRST_ITEM_POS = Position(45, 52)
    EMPTY_SLOT_IMAGE = load_image(containers_path + 'emptyslot.png')

    def __init__(self, position: Position, origin_image: numpy.ndarray):
        self.position = position
        self._is_empty = Container._check_if_empty(position, origin_image)

    @staticmethod
    def _check_if_empty(position: Position, origin_image: numpy.ndarray) -> bool:
        first_item = origin_image[
                     position.y: position.y + Container.FIRST_ITEM_POS.y,
                     position.x: position.x + Container.FIRST_ITEM_POS.x
                     ]
        return not locate_image(first_item, Container.EMPTY_SLOT_IMAGE).is_empty()

    @staticmethod
    def find_first(window_state: State[Window], container_img: numpy.ndarray) -> Optional['Container']:
        origin = window_state.get().ndarray()
        container_pos = locate_image(origin, container_img, precision=0.92)
        return Container(container_pos, origin)

    @staticmethod
    def find_all(window_state: State[Window], container_img: numpy.ndarray) -> Generator['Container', None, None]:
        origin = window_state.get().ndarray()
        positions = locate_image_gen(origin, container_img, precision=0.92)
        return (Container(pos, origin) for pos in positions if pos)

    @staticmethod
    def find_first_not_empty(window_state: State[Window], container_img: numpy.ndarray) -> Optional['Container']:
        for container in Container.find_all(window_state, container_img):
            if not container.is_empty():
                return container
        return None

    def is_empty(self) -> bool:
        return self._is_empty

    def __repr__(self):
        return self.__class__.__name__ \
               + '(' + self.position.__repr__() \
               + ', is_empty: ' + str(self.is_empty()) \
               + ')'
