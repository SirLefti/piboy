from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFont
from app.BaseApp import BaseApp
import config
import time
from datetime import datetime


def watch_function():
    while True:
        now = datetime.now()
        # wait for next minute
        time.sleep(60 - now.second - now.microsecond / 1000000.0)
        date_str = datetime.now().strftime('%d-%m-%Y %H:%M')
        update_display(config.INTERFACE.resolution, config.APPS, 0, date_str)


def update_display(resolution: Tuple[int, int], apps: List[BaseApp], active_app, date_str):
    """Draw call than handles the complete cycle of drawing a new image to the display."""
    image = Image.new('RGB', resolution, config.BACKGROUND)
    draw_buffer = ImageDraw.Draw(image)
    draw_base(draw_buffer, resolution, apps, active_app=active_app, date_str=date_str)
    apps[active_app].draw(draw_buffer)
    interface.show(image)


def draw_base(draw: ImageDraw, resolution: Tuple[int, int], apps: List[BaseApp], active_app, date_str) -> ImageDraw:
    w, h = resolution
    head_v_offset = 26  # base line for header
    head_h_offset = 50  # spacing to the sides
    v_limit = 5  # vertical limiter line
    app_space = 20  # space between app headers
    app_pad = 5  # space around app header
    foot_height = 20  # height of the footer
    foot_v_offset = 3  # spacing to the bottom
    foot_h_offset = head_h_offset  # spacing to the sides

    # draw base header lines
    draw.line((head_h_offset, head_v_offset, w - head_h_offset, head_v_offset), fill=config.ACCENT)
    draw.line((head_h_offset, head_v_offset, head_h_offset, head_v_offset + v_limit), fill=config.ACCENT)
    draw.line((w - head_h_offset, head_v_offset, w - head_h_offset, head_v_offset + v_limit), fill=config.ACCENT)

    # draw app short name header
    font = ImageFont.truetype(config.FONT, 16)
    cursor = head_h_offset + app_space
    for index, app in enumerate(apps):
        t_w, t_h = font.getsize(app.title)
        draw.text((cursor, head_v_offset - t_h - app_pad), app.title, config.ACCENT, font=font)
        if index == active_app:
            draw.line((cursor - app_pad, head_v_offset, cursor + t_w + app_pad, head_v_offset), fill=config.BACKGROUND)
            draw.line((cursor - app_pad, head_v_offset, cursor - app_pad, head_v_offset - v_limit), fill=config.ACCENT)
            draw.line((cursor + t_w + app_pad, head_v_offset, cursor + t_w + app_pad, head_v_offset - v_limit), fill=config.ACCENT)
        cursor = cursor + t_w + app_space

    # draw footer
    draw.rectangle((foot_h_offset, h - foot_height - foot_v_offset, w - foot_h_offset, h - foot_v_offset), fill=config.ACCENT_INACTIVE)
    t_w, t_h = font.getsize(date_str)
    t_pad = (foot_height - t_h) / 2
    draw.text((w - foot_h_offset - t_pad - t_w, h - foot_height - foot_v_offset + t_pad), date_str, config.ACCENT, font=font)
    return draw


if __name__ == '__main__':
    interface = config.INTERFACE

    # initial draw
    last_date_str = datetime.now().strftime('%d-%m-%Y %H:%M')
    last_active_app = 0
    update_display(interface.resolution, config.APPS, active_app=last_active_app, date_str=last_date_str)

    # blocking function that updates the clock
    watch_function()
