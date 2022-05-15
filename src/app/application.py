from typing import Type, Dict

import attr
from yaml import safe_load as yaml_load, YAMLError

from app.context import Context
from app.gui import Gui, GuiHandlerRegistry
from app.logger import Logger


@attr.s
class Application:
    from app.module import Module
    context = attr.ib(type=Context, init=False)
    gui = attr.ib(type=Gui, init=False)
    modules = attr.ib(type=Dict[Type[Module], Module], factory=dict)

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
        self.modules = {module: module.load(config, self.context) for module in ModuleRegistry.modules}
        [Logger.log(module.name() + " loaded!") for module in self.modules.keys()]
        Logger.log("Application initialized!")
        self.gui = Gui(self.context.game)
        [self.gui.register_handler(handler.create(self.modules)) for handler in GuiHandlerRegistry.handlers]

    def run(self):
        self.gui.show()
        self.context.game.start_all()
        self.context.game.await_exit()
