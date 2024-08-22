from core.decorator import override
from interface.Interface import Interface
from PIL import Image


class PillowInterface(Interface):

    @override
    def close(self):
        pass

    @override
    def show(self, image: Image.Image, x0, y0):
        image.show()
