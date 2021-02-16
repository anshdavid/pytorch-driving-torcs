import mss
import mss.tools
import numpy as np

class ScreenGrab:

    def __init__(self, monitor=1, width=800, height=600) -> None:

        self.sct = mss.mss()

        mon = self.sct.monitors[monitor]

        self.monitor = {
                "top": mon["top"] + 1080 - height,
                "left": mon["left"],
                "width": width,
                "height": height,
                "mon": monitor,}


    def GrabRGB(self):
        # BGR->RGB
        return np.array(
            self.sct.grab(self.monitor), dtype=np.uint8)[..., [0, 1, 2]]

    def GrabBGR(self):
        return np.array(
            self.sct.grab(self.monitor), dtype=np.uint8)