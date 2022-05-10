import attr
from yaml import safe_load as yaml_load, YAMLError

from app.gui import Gui, GuiHandlerRegistry
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

    @staticmethod
    def create(config: dict) -> 'Context':
        game_title = config['title']
        return Context(game_title)


@attr.s
class Application:
    context = attr.ib(type=Context, init=False)
    gui = attr.ib(type=Gui, init=False)

    def _load_config(self, config_path: str) -> dict:
        with open(config_path, "r") as stream:
            try:
                return yaml_load(stream)
            except YAMLError as exc:
                raise RuntimeError("Unable to load app: " + config_path + ". Reason: " + str(exc))

    def init(self, config_path: str):
        config = self._load_config(config_path)
        self.context = Context.create(config)
        from app.module import ModuleRegistry
        [print(module.load(config, self.context).name(), "loaded!") for module in ModuleRegistry.modules]
        print("Application initialized!")
        self.gui = Gui()
        [self.gui.register_handler(handler()) for handler in GuiHandlerRegistry.handlers]

    def run(self):
        self.gui.show()
        self.context.game.start_all()
        self.context.game.await_exit()
