from typing import Type, List, Dict, Optional

import PySimpleGUI as sg
import attr

from app.logger import LogWriter, LogLevel, Logger
from app.module import Module
from domain.game.game import Game
from util.task import StoppableThread


class Switches:
    TITLE = 'Switches'
    TARGET = 'Target'
    LOOT = 'Loot'
    COMBO = 'Combo'
    MAGIC = 'Magic'


class Say:
    TITLE = 'Say'
    INPUT_KEY = '-SAY-'
    BUTTON = 'Submit text'


class Logs:
    TITLE = 'Logs'
    OUTPUT_KEY = '-LOG-'


@attr.s
class GuiHandler:

    @classmethod
    def create(cls, modules: Dict[Type[Module], Module]) -> 'GuiHandler':
        raise NotImplementedError()

    def handle(self, window: sg.Window, event: str, values: dict) -> None:
        raise NotImplementedError()

    def can_handle(self) -> str:
        raise NotImplementedError()


class GuiHandlerRegistry:
    handlers: List[Type[GuiHandler]] = list()

    @staticmethod
    def register(cls: Type[GuiHandler]):
        GuiHandlerRegistry.handlers.append(cls)


@GuiHandlerRegistry.register
@attr.s
class ComboGuiHandler(GuiHandler):
    from app.module import Combo
    combo = attr.ib(type=Combo)

    @classmethod
    def create(cls, modules: Dict[Type[Module], Module]) -> 'ComboGuiHandler':
        from app.module import Combo
        combo = modules.get(Combo)
        return cls(combo)

    def handle(self, window: sg.Window, event: str, values: dict) -> None:
        self.combo.switch()

    def can_handle(self) -> str:
        return Switches.COMBO


@GuiHandlerRegistry.register
@attr.s
class AutoTargetGuiHandler(GuiHandler):
    from app.module import AutoTarget
    autotarget = attr.ib(type=AutoTarget)

    @classmethod
    def create(cls, modules: Dict[Type[Module], Module]) -> 'AutoTargetGuiHandler':
        from app.module import AutoTarget
        autotarget = modules.get(AutoTarget)
        return cls(autotarget)

    def handle(self, window: sg.Window, event: str, values: dict) -> None:
        self.autotarget.switch()

    def can_handle(self) -> str:
        return Switches.TARGET


@GuiHandlerRegistry.register
@attr.s
class AutoLootGuiHandler(GuiHandler):
    from app.module import AutoLoot
    autoloot = attr.ib(type=AutoLoot)

    @classmethod
    def create(cls, modules: Dict[Type[Module], Module]) -> 'AutoLootGuiHandler':
        from app.module import AutoLoot
        autoloot = modules.get(AutoLoot)
        return cls(autoloot)

    def handle(self, window: sg.Window, event: str, values: dict) -> None:
        self.autoloot.switch()

    def can_handle(self) -> str:
        return Switches.LOOT

@GuiHandlerRegistry.register
@attr.s
class MagicTrainingGuiHandler(GuiHandler):
    from app.module import MagicTraining
    magictraining = attr.ib(type=MagicTraining)

    @classmethod
    def create(cls, modules: Dict[Type[Module], Module]) -> 'MagicTrainingGuiHandler':
        from app.module import MagicTraining
        magictraining = modules.get(MagicTraining)
        return cls(magictraining)

    def handle(self, window: sg.Window, event: str, values: dict) -> None:
        self.magictraining.switch()

    def can_handle(self) -> str:
        return Switches.MAGIC


@attr.s(hash=True)
class GuiLogWriter(LogWriter):
    window = attr.ib(type=sg.Window)

    def write(self, msg: str, lvl: LogLevel):
        if lvl.value >= LogLevel.INFO.value and not self.window.is_closed():
            try:
                self.window[Logs.OUTPUT_KEY].update(lvl.name + ": " + msg)
            except RuntimeError:
                pass


@GuiHandlerRegistry.register
@attr.s
class SayGuiHandler(GuiHandler):
    from app.module import Chat
    chat = attr.ib(type=Chat)

    @classmethod
    def create(cls, modules: Dict[Type[Module], Module]) -> 'SayGuiHandler':
        from app.module import Chat
        chat = modules.get(Chat)
        return cls(chat)

    def handle(self, window: sg.Window, event: str, values: dict) -> None:
        msg = values[Say.INPUT_KEY]
        self.chat.chat_handler.say(msg)
        window[Say.INPUT_KEY].update('')

    def can_handle(self) -> str:
        return Say.BUTTON


@attr.s
class Gui:
    game = attr.ib(type=Game)
    title = attr.ib(default='RBot')
    handlers = attr.ib(type=Dict[str, GuiHandler], factory=dict)
    thread = attr.ib(default=None, type=StoppableThread, init=False)
    window = attr.ib(type=sg.Window, init=False)

    def show(self):
        self.window = self._create_window(self.title)
        Logger.register(GuiLogWriter(self.window))
        self.thread = StoppableThread(target=self._run_event_loop, args=(), daemon=True)
        self.thread.start()

    def _create_window(self, title: str) -> sg.Window:
        switches_column = [
            [sg.Text(Switches.TITLE)],
            [sg.Button(Switches.TARGET, size=(6, 1), pad=(0, 0))],
            [sg.Button(Switches.LOOT, size=(6, 1), pad=(0, 0))],
            [sg.Button(Switches.COMBO, size=(6, 1), pad=(0, 0))],
            [sg.Button(Switches.MAGIC, size=(6, 1), pad=(0, 0), )],
        ]

        say_column = [
            [sg.Text(Say.TITLE), sg.Input(size=(24, 1), key=Say.INPUT_KEY)],
            # [sg.Input(size=(20, 1), key=Say.INPUT_KEY)],
            [sg.Button(Say.BUTTON, visible=False, bind_return_key=True)],
            # [sg.HSeparator],
            [sg.Text(Logs.TITLE)],
            [sg.Multiline(size=(30, 4), key=Logs.OUTPUT_KEY, no_scrollbar=True)],
        ]

        # ----- Full layout -----
        layout = [
            [
                sg.Column(switches_column, element_justification='center'),
                sg.VSeperator(),
                sg.Column(say_column),
            ]
        ]
        # Create the window
        return sg.Window(title, layout, keep_on_top=True, margins=(0, 0))

    def register_handler(self, handler: GuiHandler):
        self.handlers[handler.can_handle()] = handler

    def close(self):
        if self.thread:
            self.thread.stop()
        self.game.exit()
        self.window.close()

    def _run_event_loop(self):
        # Create an event loop
        while True:
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                break
            handler: Optional[GuiHandler] = self.handlers.get(event)
            if handler:
                handler.handle(self.window, event, values)
        self.close()
