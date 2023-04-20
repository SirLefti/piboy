from app.App import App
from PIL import Image, ImageDraw
import config


class DebugApp(App):

    def __init__(self):
        self.__button_left = False
        self.__button_right = False
        self.__button_up = False
        self.__button_down = False
        self.__button_a = False
        self.__button_b = False

    @property
    def title(self) -> str:
        return 'DBG'

    def draw(self, image: Image, partial=False) -> (Image, int, int):
        width, height = config.RESOLUTION
        center_x, center_y = int(width / 2), int(height / 2)

        dpad_offset = 40
        dpad_spacing = 20
        action_offset = 40
        action_spacing = 20
        button_size = 30

        draw = ImageDraw.Draw(image)

        points_left = [
            (center_x - dpad_offset - dpad_spacing, center_y - button_size / 2),
            (center_x - dpad_offset - dpad_spacing, center_y + button_size / 2),
            (center_x - dpad_offset - dpad_spacing - button_size, center_y)
        ]
        draw.polygon(points_left, fill=(config.ACCENT if self.__button_left else config.ACCENT_DARK))

        points_right = [
            (center_x - dpad_offset + dpad_spacing, center_y - button_size / 2),
            (center_x - dpad_offset + dpad_spacing, center_y + button_size / 2),
            (center_x - dpad_offset + dpad_spacing + button_size, center_y)
        ]
        draw.polygon(points_right, fill=(config.ACCENT if self.__button_right else config.ACCENT_DARK))

        points_up = [
            (center_x - dpad_offset - button_size / 2, center_y - dpad_spacing),
            (center_x - dpad_offset + button_size / 2, center_y - dpad_spacing),
            (center_x - dpad_offset, center_y - dpad_spacing - button_size)
        ]
        draw.polygon(points_up, fill=(config.ACCENT if self.__button_up else config.ACCENT_DARK))

        points_down = [
            (center_x - dpad_offset - button_size / 2, center_y + dpad_spacing),
            (center_x - dpad_offset + button_size / 2, center_y + dpad_spacing),
            (center_x - dpad_offset, center_y + dpad_spacing + button_size)
        ]
        draw.polygon(points_down, fill=(config.ACCENT if self.__button_down else config.ACCENT_DARK))

        points_a = ((center_x + action_offset - button_size / 2, center_y - action_spacing / 2),
                    (center_x + action_offset + button_size / 2, center_y - button_size - action_spacing / 2))
        draw.rectangle(points_a, fill=(config.ACCENT if self.__button_a else config.ACCENT_DARK))

        points_b = ((center_x + action_offset - button_size / 2, center_y + action_spacing / 2),
                    (center_x + action_offset + button_size / 2, center_y + button_size + action_spacing / 2))
        draw.rectangle(points_b, fill=(config.ACCENT if self.__button_b else config.ACCENT_DARK))

        if partial:
            points_all = [*points_left, *points_right, *points_up, *points_down, *points_a, *points_b]
            max_x = max(points_all, key=lambda e: e[0])[0]
            max_y = max(points_all, key=lambda e: e[1])[1]
            min_x = min(points_all, key=lambda e: e[0])[0]
            min_y = min(points_all, key=lambda e: e[1])[1]
            return image.crop((min_x, min_y) + (max_x, max_y)), min_x, min_y
        else:
            return image, 0, 0

    def on_key_left(self):
        self.__button_left = True
        self.__button_right = False
        self.__button_up = False
        self.__button_down = False
        self.__button_a = False
        self.__button_b = False

    def on_key_right(self):
        self.__button_left = False
        self.__button_right = True
        self.__button_up = False
        self.__button_down = False
        self.__button_a = False
        self.__button_b = False

    def on_key_up(self):
        self.__button_left = False
        self.__button_right = False
        self.__button_up = True
        self.__button_down = False
        self.__button_a = False
        self.__button_b = False

    def on_key_down(self):
        self.__button_left = False
        self.__button_right = False
        self.__button_up = False
        self.__button_down = True
        self.__button_a = False
        self.__button_b = False

    def on_key_a(self):
        self.__button_left = False
        self.__button_right = False
        self.__button_up = False
        self.__button_down = False
        self.__button_a = True
        self.__button_b = False

    def on_key_b(self):
        self.__button_left = False
        self.__button_right = False
        self.__button_up = False
        self.__button_down = False
        self.__button_a = False
        self.__button_b = True

    def on_app_enter(self):
        pass

    def on_app_leave(self):
        self.__button_left = False
        self.__button_right = False
        self.__button_up = False
        self.__button_down = False
        self.__button_a = False
        self.__button_b = False
