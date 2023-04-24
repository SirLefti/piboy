from app.App import SelfUpdatingApp
from PIL import Image, ImageDraw
from typing import Callable, Any
from datetime import datetime
import math
import config


class ClockApp(SelfUpdatingApp):

    def __init__(self, update_callback: Callable[[Any], None]):
        super().__init__(self.__draw_partial)
        self.__update_callback = update_callback

    def __draw_partial(self):
        self.__update_callback({'partial': True})

    @property
    def title(self) -> str:
        return 'CLK'

    def draw(self, image: Image, partial=False) -> (Image, int, int):
        width, height = config.RESOLUTION
        center_x, center_y = int(width / 2), int(height / 2)
        size = 200
        quarters_length = 15
        five_minutes_length = 7
        h_length = 40
        m_length = 60
        s_length = 80

        now = datetime.now()
        draw = ImageDraw.Draw(image)

        radius = int(size / 2)
        left = center_x - radius
        top = center_y - radius
        right = center_x + radius
        bottom = center_y + radius

        # clock body
        draw.ellipse([(left, top), (right, bottom)], outline=config.ACCENT, width=2)

        for d in range(12):
            angle = (d + 1) * int(360 / 12)
            length = quarters_length if (d + 1) % 3 == 0 else five_minutes_length
            start_x = center_x + (radius - length) * math.sin(math.radians(angle))
            start_y = center_y + (radius - length) * math.cos(math.radians(angle))
            end_x = center_x + radius * math.sin(math.radians(angle))
            end_y = center_y + radius * math.cos(math.radians(angle))
            draw.line((start_x, start_y) + (end_x, end_y), fill=config.ACCENT)

        # clock hands
        h_angle = (now.hour / 12) * 360 + (now.minute / 60 / 12) * 360 + (now.second / 60 / 60 / 12) * 360 + 180
        m_angle = (now.minute / 60) * 360 + (now.second / 60 / 60) * 360 + 180
        s_angle = (now.second / 60) * 360 + 180

        h_x = h_length * math.sin(math.radians(-h_angle))
        h_y = h_length * math.cos(math.radians(h_angle))
        draw.line(((center_x, center_y) + (center_x + h_x, center_y + h_y)), fill=config.ACCENT)

        m_x = m_length * math.sin(math.radians(-m_angle))
        m_y = m_length * math.cos(math.radians(m_angle))
        draw.line(((center_x, center_y) + (center_x + m_x, center_y + m_y)), fill=config.ACCENT)

        s_x = s_length * math.sin(math.radians(-s_angle))
        s_y = s_length * math.cos(math.radians(s_angle))
        draw.line(((center_x, center_y) + (center_x + s_x, center_y + s_y)), fill=config.ACCENT)

        if partial:
            return image.crop(((left, top) + (right, bottom))), left, top
        else:
            return image, 0, 0

    def on_key_left(self):
        pass

    def on_key_right(self):
        pass

    def on_key_up(self):
        pass

    def on_key_down(self):
        pass

    def on_key_a(self):
        pass

    def on_key_b(self):
        pass

    @property
    def refresh_time(self) -> float:
        return 1.0
