from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFont
from app.BaseApp import BaseApp
import config
import time
from datetime import datetime


ACTIVE_APP = 0


def on_key_left():
    config.APPS[ACTIVE_APP].on_key_left()
    update_display()


def on_key_up():
    config.APPS[ACTIVE_APP].on_key_up()
    update_display()


def on_key_right():
    config.APPS[ACTIVE_APP].on_key_right()
    update_display()


def on_key_down():
    config.APPS[ACTIVE_APP].on_key_down()
    update_display()


def on_key_a():
    config.APPS[ACTIVE_APP].on_key_a()
    update_display()


def on_key_b():
    config.APPS[ACTIVE_APP].on_key_b()
    update_display()


def on_rotary_increase():
    global ACTIVE_APP
    ACTIVE_APP += 1
    # go to first app if last was selected
    if not ACTIVE_APP < len(config.APPS):
        ACTIVE_APP = 0
    update_display()


def on_rotary_decrease():
    global ACTIVE_APP
    ACTIVE_APP -= 1
    # go to last app if first was selected
    if ACTIVE_APP < 0:
        ACTIVE_APP = len(config.APPS) - 1
    update_display()


def watch_function():
    while True:
        now = datetime.now()
        # wait for next minute
        time.sleep(60 - now.second - now.microsecond / 1000000.0)
        update_display()


def update_display():
    """Draw call than handles the complete cycle of drawing a new image to the display."""
    image = Image.new('RGB', config.INTERFACE.resolution, config.BACKGROUND)
    draw_buffer = ImageDraw.Draw(image)
    date_str = datetime.now().strftime('%d-%m-%Y %H:%M')
    draw_base(draw_buffer, config.INTERFACE.resolution, config.APPS, active_app=ACTIVE_APP, date_str=date_str)
    config.APPS[ACTIVE_APP].draw(draw_buffer)
    config.INTERFACE.show(image)


def draw_base(draw: ImageDraw, resolution: Tuple[int, int], apps: List[BaseApp], active_app, date_str) -> ImageDraw:
    width, height = resolution
    vertical_line = 5  # vertical limiter line
    header_top_offset = config.APP_TOP_OFFSET - vertical_line  # base for header
    header_side_offset = config.APP_SIDE_OFFSET  # spacing to the sides
    app_spacing = 20  # space between app headers
    app_padding = 5  # space around app header
    footer_height = 20  # height of the footer
    footer_bottom_offset = 3  # spacing to the bottom
    footer_side_offset = header_side_offset  # spacing to the sides

    # draw base header lines
    start = (header_side_offset, header_top_offset + vertical_line)
    end = (header_side_offset, header_top_offset)
    draw.line(start + end, fill=config.ACCENT)
    start = end
    end = (width - header_side_offset, header_top_offset)
    draw.line(start + end, fill=config.ACCENT)
    start = end
    end = (width - header_side_offset, header_top_offset + vertical_line)
    draw.line(start + end, fill=config.ACCENT)

    # draw app short name header
    font = ImageFont.truetype(config.FONT, 16)
    max_text_width = width - (2 * header_side_offset)
    app_text_width = sum(font.getsize(app.title)[0] for app in apps) + (len(apps) - 1) * app_spacing
    cursor = header_side_offset + (max_text_width - app_text_width) / 2
    for index, app in enumerate(apps):
        text_width, text_height = font.getsize(app.title)
        draw.text((cursor, header_top_offset - text_height - app_padding), app.title, config.ACCENT, font=font)
        if index == active_app:
            start = (cursor - app_padding, header_top_offset - vertical_line)
            end = (cursor - app_padding, header_top_offset)
            draw.line(start + end, fill=config.ACCENT)
            start = end
            end = (cursor + text_width + app_padding, header_top_offset)
            draw.line(start + end, fill=config.BACKGROUND)
            start = end
            end = (cursor + text_width + app_padding, header_top_offset - vertical_line)
            draw.line(start + end, fill=config.ACCENT)
        cursor = cursor + text_width + app_spacing

    # draw footer
    start = (footer_side_offset, height - footer_height - footer_bottom_offset)
    end = (width - footer_side_offset, height - footer_bottom_offset)
    draw.rectangle(start + end, fill=config.ACCENT_DARK)
    text_width, text_height = font.getsize(date_str)
    text_padding = (footer_height - text_height) / 2
    draw.text((width - footer_side_offset - text_padding - text_width, height - footer_height - footer_bottom_offset +
               text_padding), date_str, config.ACCENT, font=font)
    return draw


if __name__ == '__main__':
    interface = config.INTERFACE

    # initial draw
    last_date_str = datetime.now().strftime('%d-%m-%Y %H:%M')
    update_display()

    # blocking function that updates the clock
    watch_function()
