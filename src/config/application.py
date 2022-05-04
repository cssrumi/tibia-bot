import attr

from ctx.player import PlayerStateManager, PlayerImageListener
from ctx.window import WindowStateManager
from domain.battle import BattleListStateManager, BattleList
from domain.game.game import Game


@attr.s
class Context:
    game_title = attr.ib(type=str)
    game = attr.ib(type=Game, init=False)
    window_state_manager = attr.ib(type=WindowStateManager, init=False)
    player_state_manager = attr.ib(type=PlayerStateManager, init=False)
    battle_state_manager = attr.ib(type=BattleListStateManager, init=False)

    def __attrs_post_init__(self):
        self.game = Game(self.game_title)
        self.window_state_manager = WindowStateManager(self.game, delay=0)
        self.player_state_manager = PlayerStateManager()
        pil = PlayerImageListener(self.player_state_manager)
        self.window_state_manager.add_update_listener(pil.update_listener)
        battle = BattleList(self.game, self.window_state_manager)
        self.battle_state_manager = BattleListStateManager(battle)


@attr.s
class Application:
    game = attr.ib(type=Game)
    context = attr.ib(type=Context)

    def init_context(self, config: dict):
        self.context

    def run(self):
        self.game.start_all()
        self.game.await_exit()
