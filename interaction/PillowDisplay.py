from core.decorator import override
from interaction.Display import Display
from PIL import Image


class PillowDisplay(Display):

    @override
    def close(self):
        pass

    @override
    def show(self, image: Image.Image, x0: int, y0: int):
        image.show()
