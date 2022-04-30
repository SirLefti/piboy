from PIL import Image, ImageDraw
import config

BACKGROUND = (0, 0, 0)
ACCENT = (27, 251, 30)
ACCENT_INACTIVE = (9, 64, 9)


def draw_base(draw: ImageDraw, resolution) -> ImageDraw:
    header_height = 26
    edge_offset = 50
    return draw.line((edge_offset, header_height, resolution[0] - edge_offset, header_height), fill=ACCENT)


if __name__ == '__main__':
    interface = config.INTERFACE
    image = Image.new('RGB', interface.resolution, BACKGROUND)
    draw_buffer = ImageDraw.Draw(image)
    draw_base(draw_buffer, interface.resolution)
    interface.show(image)
    while True:
        pass
