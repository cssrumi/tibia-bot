import attr
from PIL.Image import Image

from domain.game.grab import ApplicationGrabber, create_grabber
from domain.state import StateManagerTask


@attr.s
class WindowStateManagerTask(StateManagerTask[Image]):
    grabber = attr.ib(type=ApplicationGrabber, init=False)

    def __attrs_post_init__(self):
        self.game.add_task(self)
        self.grabber = create_grabber(self.game.name)

    def new_value(self) -> Image:
        return self.grabber.grab()
