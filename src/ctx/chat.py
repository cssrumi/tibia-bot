import time
from enum import Enum

import attr

from app.logger import Logger
from ctx.player import PlayerStateManager
from domain.game.control import Keys
from domain.game.game import Game


class Channel(Enum):
    DEFAULT = 0


@attr.s
class Chat:
    game = attr.ib(type=Game)
    psm = attr.ib(type=PlayerStateManager)
    delay = attr.ib(type=float, default=0.1)

    def say(self, msg: str, channel: Channel = Channel.DEFAULT):
        if channel is not Channel.DEFAULT:
            raise RuntimeError("unsupported channel type")
        player_state = self.psm.get()
        while player_state.is_empty() or not player_state.get().is_healthy():
            time.sleep(self.delay)
        self.game.controller.press(Keys.ENTER)
        time.sleep(self.delay)
        self.game.controller.write(msg)
        self.game.controller.press(Keys.ENTER)
        Logger.info(f"Chat {channel}: {msg}")
