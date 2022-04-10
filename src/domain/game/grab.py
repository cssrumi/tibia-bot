from ctypes import windll

import attr
import win32gui
import win32ui
from PIL import Image, ImageGrab

tibia_hwnd = win32gui.FindWindowEx(None, None, None, 'Tibia - Mietar')


@attr.s
class ApplicationGrabber:
    name = attr.ib(type=str)

    def grab(self):
        raise NotImplementedError()


@attr.s
class PilApplicationGrabber(ApplicationGrabber):

    def grab(self):
        return ImageGrab.grab()


@attr.s
class Win32ApplicationGrabber(ApplicationGrabber):
    hwnd = attr.ib(init=False)
    w = attr.ib(init=False)
    h = attr.ib(init=False)

    def __attrs_post_init__(self):
        self.hwnd = win32gui.FindWindowEx(None, None, None, self.name)
        left, top, right, bot = win32gui.GetWindowRect(self.hwnd)
        self.w = right - left
        self.h = bot - top

    def grab(self):
        hwnd = self.hwnd
        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()

        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, self.w, self.h)

        saveDC.SelectObject(saveBitMap)
        windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 0)

        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)

        img = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1)

        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)
        return img


def create_grabber(app_name: str) -> ApplicationGrabber:
    return Win32ApplicationGrabber(app_name)
