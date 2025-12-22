import mss
import numpy as np
import win32gui


class ScreenCapture:
    def __init__(self, window_name):
        self.window_name = window_name
        self.sct = mss.mss()
        self.hwnd = win32gui.FindWindow(None, window_name)

        if not self.hwnd:
            raise RuntimeError(f"No se encontro la ventana: {window_name}")

    def _get_window_rect(self):
        left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
        return {
            "left": left,
            "top": top,
            "width": right - left,
            "height": bottom - top,
        }

    def grab(self):
        monitor = self._get_window_rect()
        img = self.sct.grab(monitor)
        return np.array(img)[:, :, :3]  # BGR compatible

    def release(self):
        self.sct.close()
