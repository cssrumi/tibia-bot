from typing import List, Optional

import attr
import numpy
from PIL.Image import Image

from ctx.window import WindowStateManagerTask
from domain.game.game import Game
from domain.game.locate import Position, locate_image
from domain.monster import DetectedMonster, Monster
from domain.state import State


@attr.s
class BattleList:
    game = attr.ib(type=Game)
    wsmt = attr.ib(type=WindowStateManagerTask)
    start_pos = attr.ib(default=Position.empty(), type=Position)
    end_pos = attr.ib(default=Position.empty(), type=Position)

    def _find_position(self):
        if self.game.is_active():
            state = self.wsmt.get()
            self.start_pos = locate_image(state, '../battlelist/battlelist-start')
            self.end_pos = locate_image(state, '../battlelist/battlelist-end.png', start=False)

    def detect_monsters(self, monsters: List[Monster]) -> List[DetectedMonster]:
        if not self._positions_found():
            self._find_position()
        if not self._positions_found():
            return []
        pass

    def _battle_list(self) -> Optional[numpy.ndarray]:
        if not self.game.is_active():
            return
        state = self.wsmt.get()
        # return state[]
        pass

    def _positions_found(self):
        return not self.start_pos.is_empty() and not self.start_pos.is_empty()
