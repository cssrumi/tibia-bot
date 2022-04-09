import attr
from PIL import ImageGrab
from PIL.Image import Image

from domain.state import StateManagerTask


@attr.s
class WindowStateManagerTask(StateManagerTask[Image]):

    def __attrs_post_init__(self):
        self.game.add_task(self)

    def new_value(self) -> Image:
        return ImageGrab.grab()
