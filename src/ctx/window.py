import attr
from PIL import ImageGrab
from PIL.Image import Image

from state import StateManagerTask


@attr.s
class Window(StateManagerTask[Image]):

    def new_value(self) -> Image:
        return ImageGrab.grab()
