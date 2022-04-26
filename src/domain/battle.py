from typing import List, Optional

import attr
import numpy

from ctx.window import WindowStateManagerTask
from domain.game.game import Game
from domain.game.locate import Position, locate_image, load_image
from domain.monster import DetectedMonster, Monster


@attr.s
class BattleList:
    game = attr.ib(type=Game)
    wsmt = attr.ib(type=WindowStateManagerTask)
    start_pos = attr.ib(default=Position.empty(), type=Position)
    end_pos = attr.ib(default=Position.empty(), type=Position)

    def _find_position(self):
        if self.game.is_active():
            window_state = self.wsmt.get()
            origin = window_state.get().ndarray()
            self.start_pos = locate_image(origin, '../battlelist/battlelist-start')
            battle_origin = origin[self.start_pos.y:, self.start_pos.x:]
            battle_end_template = load_image('../battlelist/battlelist-end.png')
            end_pos = locate_image(battle_origin, battle_end_template, start=False)
            _, width = battle_end_template.shape
            self.end_pos = end_pos.plus(Position(width, 0))

    def detect_monsters(self, filters: List[Monster] = None) -> List[DetectedMonster]:
        if not self._positions_found():
            self._find_position()
        if not self._positions_found():
            return []
        return self._find_filtered(filters) if filters else self._find_all()

    def _find_filtered(self, filters: List[Monster]) -> List[DetectedMonster]:
        raise NotImplemented()

    def _find_all(self) -> List[DetectedMonster]:
        raise NotImplemented()

    def _battle_list(self) -> Optional[numpy.ndarray]:
        if not self.game.is_active() or not self._positions_found():
            return
        state = self.wsmt.get()
        origin = state.get().ndarray()
        return origin[self.start_pos.y:self.end_pos.y, self.start_pos.x:self.end_pos.x]

    def _positions_found(self):
        return not self.start_pos.is_empty() and not self.start_pos.is_empty()
