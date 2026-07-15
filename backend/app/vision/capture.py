from mss import mss
from PIL import Image
from pathlib import Path
import time

class ScreenCapture:
    def __init__(self):
        self.sct = mss()

    def capture(self):
        monitor =self.sct.monitors[1] #Primary monitor
        screenshot=self.sct.grab(monitor)
        image=Image.frombytes(
            "RGB",
            screenshot.size,
            screenshot.rgb,
        )
        return image
    
    def save(self,image):
        save_dir=Path("screenshots")
        save_dir.mkdir(exist_ok=True)
        filename=save_dir / f"{int(time.time())}.png"
        image.save(filename)
        return str(filename)
