from typing import List, Optional

import attr
import cv2
import numpy
from PIL import Image

from ctx.window import WindowStateManagerTask
from domain.game.game import Game
from domain.game.locate import Position, locate_image, load_image, locate_image_gen
from domain.monster import DetectedMonster, Monster
from domain.state import StateManagerTask


MARGIN = Position(8, 31)


class BattleListElements:
    _BATTLE_PREFIX = '../image/battlelist/'
    START = _BATTLE_PREFIX + 'battlelist-start.png'
    END = _BATTLE_PREFIX + 'battlelist-end.png'
    ATTACKED = _BATTLE_PREFIX + 'attacked.png'
    MONSTER = _BATTLE_PREFIX + 'monster.png'


@attr.s
class BattleList:
    game = attr.ib(type=Game)
    wsmt = attr.ib(type=WindowStateManagerTask)
    start_pos = attr.ib(default=Position.empty(), type=Position)
    fixed_start_pos = attr.ib(default=Position.empty(), type=Position)
    end_pos = attr.ib(default=Position.empty(), type=Position)
    attacked_img = attr.ib(init=False, type=numpy.ndarray)
    monster_img = attr.ib(init=False, type=numpy.ndarray)

    def __attrs_post_init__(self):
        self.attacked_img = load_image(BattleListElements.ATTACKED, cv2.COLOR_BGR2GRAY)
        self.monster_img = load_image(BattleListElements.MONSTER, cv2.COLOR_BGR2GRAY)

    def _find_position(self):
        if not self.game.is_connected():
            return
        window_state = self.wsmt.get()
        if window_state.is_empty():
            return
        origin = window_state.get().ndarray()
        # Image.fromarray(origin).show()
        self.start_pos = locate_image(origin, BattleListElements.START)
        self.fixed_start_pos = self.start_pos.minus(MARGIN)
        battle_origin = origin[self.start_pos.y:, self.start_pos.x:]
        battle_end_template = load_image(BattleListElements.END)
        end_pos = locate_image(battle_origin, battle_end_template, start=False)
        _, width = battle_end_template.shape
        self.end_pos = end_pos.plus(Position(width, 0))

    def detect_monsters(self, filters: List[Monster] = None) -> List[DetectedMonster]:
        if not self._positions_found():
            self._find_position()
        if not self._positions_found():
            print("Battle position not found")
            return []
        return self._find_filtered(filters) if filters else self._find_all()

    def _find_filtered(self, filters: List[Monster]) -> List[DetectedMonster]:
        raise NotImplemented()

    def _find_all(self) -> List[DetectedMonster]:
        battle_list = self._battle_list()
        if battle_list is None or battle_list.size == 0:
            print("battle list is empty")
            return []
        monsters = [
            DetectedMonster(monster_pos.plus(self.fixed_start_pos), Monster.UNKNOWN, False)
            for monster_pos in locate_image_gen(
                battle_list, self.monster_img, precision=0.99
            )
            if monster_pos and not monster_pos.is_empty()
        ]
        attacked_pos = locate_image(battle_list, self.attacked_img, precision=0.985)
        if not attacked_pos.is_empty():
            attacked = DetectedMonster(attacked_pos.plus(self.fixed_start_pos), Monster.UNKNOWN, True)
            monsters = list(filter(lambda m: m.position.y != attacked.position.y, monsters))
            monsters.append(attacked)
        return monsters

    def _battle_list(self) -> Optional[numpy.ndarray]:
        if not self._positions_found():
            print('Battle list not found')
            return
        state = self.wsmt.get()
        origin = state.get().ndarray_bgr()
        return origin[
               self.start_pos.y:self.start_pos.y + self.end_pos.y,
               self.start_pos.x:self.start_pos.x + self.end_pos.x
               ]

    def _positions_found(self):
        return not self.start_pos.is_empty() and not self.start_pos.is_empty()


@attr.s
class BattleListStateManager(StateManagerTask[List[DetectedMonster]]):
    battle = attr.ib(type=BattleList)
    game = attr.ib(init=False, type=Game)
    delay = attr.ib(init=False, kw_only=True, type=float, default=1.0)

    def __attrs_post_init__(self):
        self.game = self.battle.game
        self.battle.game.add_task(self)
        print(self.__class__.__name__, 'added')

    def new_value(self) -> List[DetectedMonster]:
        print("detecting monsters...")
        nv = self.battle.detect_monsters()
        print("found:", len(nv), nv)
        return nv
