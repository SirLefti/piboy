from interface.BaseInterface import BaseInterface
from PIL import Image


class PillowInterface(BaseInterface):

    def show(self, image: Image):
        image.show()
