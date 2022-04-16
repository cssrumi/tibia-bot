import atexit
import os
from threading import Lock

lock = Lock()


class WindowsInhibitor:
    __inhibited = False
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001

    @staticmethod
    def inhibit():
        if os.name != 'nt':
            print(f"Unhandled os type: {os.name}")
            return
        with lock:
            if WindowsInhibitor.__inhibited:
                return
            import ctypes
            print("Preventing Windows from going to sleep")
            ctypes.windll.kernel32.SetThreadExecutionState(
                WindowsInhibitor.ES_CONTINUOUS |
                WindowsInhibitor.ES_SYSTEM_REQUIRED
            )
            atexit.register(WindowsInhibitor.uninhibit)
            WindowsInhibitor.__inhibited = True

    @staticmethod
    def uninhibit():
        if os.name != 'nt':
            print(f"Unhandled os type: {os.name}")
            return
        import ctypes
        print("Allowing Windows to go to sleep")
        ctypes.windll.kernel32.SetThreadExecutionState(
            WindowsInhibitor.ES_CONTINUOUS
        )
