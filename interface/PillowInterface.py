from interface.Interface import Interface
from PIL import Image


class PillowInterface(Interface):

    def close(self):
        pass

    def show(self, image: Image):
        image.show()
