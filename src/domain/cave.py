import json
import os
from enum import Enum
from typing import List, TypeVar, Generic, Type

import attr

from app.logger import LogLevel, Logger
from domain.battle import BattleListStateManager
from domain.game.game import Game
from domain.game.locate import Position
from util.task import Task

T = TypeVar("T")


class Caves:
    CYCLOPS = '../cave/cyclops', 'cyclops'


def _read_field(dict_json: dict, key: str, _type: Type[T]) -> T:
    value = dict_json.get(key)
    if not value:
        raise KeyError('field is missing: ' + key)
    if not isinstance(value, _type):
        raise ValueError('invalid value type: ' + type(value) + ' for key: ' + key)
    return value


class AttackType(Enum):
    OFFENSIVE = 0
    BALANCED = 1
    DEFENSIVE = 2

    @staticmethod
    def deserialize(raw: str) -> 'AttackType':
        return AttackType[raw]


class WaypointType(Enum):
    WALK = 0

    @staticmethod
    def deserialize(raw: str) -> 'WaypointType':
        return WaypointType[raw]


@attr.s
class Waypoint:
    pos = attr.ib(type=Position)
    wp_type = attr.ib(type=WaypointType)

    @staticmethod
    def deserialize(raw: dict) -> 'Waypoint':
        x = _read_field(raw, 'x', int)
        y = _read_field(raw, 'y', int)
        p = Position(x, y)
        raw_wpt = _read_field(raw, 'waypointType', str)
        wpt = WaypointType.deserialize(raw_wpt)
        return Waypoint(p, wpt)


@attr.s
class CaveConfig:
    attack_type = attr.ib(type=AttackType)
    waypoints = attr.ib(type=List[Waypoint])

    @staticmethod
    def read(path: str, name: str) -> 'CaveConfig':
        dict_json = CaveConfig._read_json(path, name)

        raw_at = _read_field(dict_json, 'attackType', str)
        at = AttackType.deserialize(raw_at)

        raw_wps = _read_field(dict_json, 'waypoints', list)
        wps = [Waypoint.deserialize(raw_wp) for raw_wp in raw_wps]

        return CaveConfig(at, wps)

    @staticmethod
    def _read_json(path: str, name: str) -> dict:
        with open(os.path.join(path, name + '.json'), 'r+') as f:
            return json.load(f)


@attr.s
class CaveTask(Task):
    config = attr.ib(type=CaveConfig)
    blsm = attr.ib(type=BattleListStateManager)
    game = attr.ib(type=Game, init=False)

    def __attrs_post_init__(self):
        self.game = self.blsm.game
        self.game.add_task(self)

    def _run(self):
        Logger.log(self.config, lvl=LogLevel.DEBUG)
