import attr
import cv2
import numpy
from PIL.Image import Image

from domain.game.grab import ApplicationGrabber, create_grabber
from domain.game.locate import Position, locate_image, load_image, image_center
from domain.state import StateManagerTask, State


@attr.s
class Window:
    _image = attr.ib(type=Image)
    _ndarray_gray = attr.ib(type=numpy.ndarray)
    _ndarray_bgr = attr.ib(type=numpy.ndarray)

    def __bool__(self):
        return self._ndarray_gray.size != 0

    def image(self):
        return self._image

    def ndarray(self):
        return self._ndarray_gray

    def ndarray_bgr(self):
        return self._ndarray_bgr


@attr.s
class WindowStateManager(StateManagerTask[Window]):
    grabber = attr.ib(type=ApplicationGrabber, init=False)

    def __attrs_post_init__(self):
        self.game.add_task(self)
        self.grabber = create_grabber(self.game)

    def new_value(self) -> Window:
        image = self.grabber.grab()
        return Window(image, self._convert_image(image), self._convert_image(image, cv2.COLOR_RGB2BGR))

    @staticmethod
    def _convert_image(image: Image, mask: int = cv2.COLOR_RGBA2GRAY) -> numpy.ndarray:
        np_img = numpy.array(image)
        return cv2.cvtColor(np_img, mask)


screen_path = '../image/screen/'


class GameScreen:
    TOP = screen_path + 'top.png'
    BOTTOM = screen_path + 'bottom.png'
    WINDOW_TOP_MARGIN: int = 31
    WINDOW_SIDE_MARGIN: int = 8
    WINDOW_MARGIN_DELTA_POS = Position(WINDOW_SIDE_MARGIN, WINDOW_TOP_MARGIN)
    WIDTH_BOXES: int = 15
    HEIGHT_BOXES: int = 11
    WINDOW_WH_RATIO: float = WIDTH_BOXES / HEIGHT_BOXES


@attr.define
class GameBox:
    center: Position
    size: int

    def left(self) -> 'GameBox':
        return GameBox(self.center.minus(Position(self.size, 0)), self.size)

    def right(self) -> 'GameBox':
        return GameBox(self.center.plus(Position(self.size, 0)), self.size)

    def up(self) -> 'GameBox':
        return GameBox(self.center.minus(Position(0, self.size)), self.size)

    def down(self) -> 'GameBox':
        return GameBox(self.center.plus(Position(0, self.size)), self.size)


@attr.define
class GameWindow:
    center: Position
    width: int
    height: int
    box_size: int

    @staticmethod
    def from_window_state(window_state: State[Window]) -> 'GameWindow':
        top_img = load_image(GameScreen.TOP)
        origin = window_state.get().ndarray()
        top_pos = locate_image(origin, top_img, precision=0.98) \
            .minus(GameScreen.WINDOW_MARGIN_DELTA_POS)
        top_center = top_pos.plus(image_center(top_img))
        center_x = top_center.x
        top_height, _ = top_img.shape
        bottom_pos = locate_image(origin, GameScreen.BOTTOM, precision=0.98) \
            .minus(GameScreen.WINDOW_MARGIN_DELTA_POS)
        height = abs((top_pos.y + top_height) - bottom_pos.y)
        width = int(GameScreen.WINDOW_WH_RATIO * height)
        print("Game window height:", height, " width:", width)
        box_size = int(height / GameScreen.HEIGHT_BOXES)
        center_y = top_pos.y + top_height + (height / 2)
        center = Position(center_x, center_y)
        return GameWindow(center, width, height, box_size)

    def player_box(self) -> 'GameBox':
        return GameBox(self.center, self.box_size)
