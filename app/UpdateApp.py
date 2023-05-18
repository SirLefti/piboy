from app.App import App
from PIL import Image, ImageDraw
from subprocess import run, CompletedProcess
from typing import Callable, Optional
import config


class UpdateApp(App):
    LINE_HEIGHT = 20

    class Option:

        def __init__(self, name: str, action: Callable[[], Optional[CompletedProcess]]):
            self.__name = name
            self.__action = action

        @property
        def name(self) -> str:
            return self.__name

        @property
        def action(self) -> Callable[[], Optional[CompletedProcess]]:
            return self.__action

    def __init__(self):
        self.__selected_index = 0
        self.__options = [
            self.Option('fetch updates', self.__run_fetch),
            self.Option('reset changes', self.__run_reset),
            self.Option('clean files', self.__run_clean),
            self.Option('install updates', self.__run_install),
            self.Option('restart', self.__run_restart)
        ]
        self.__result = None

    @staticmethod
    def __run_fetch():
        return run(['git', 'fetch'])

    @staticmethod
    def __run_reset():
        return run(['git', 'reset', '--hard'])

    @staticmethod
    def __run_clean():
        return run(['git', 'clean', '-fd'])

    @staticmethod
    def __run_install():
        return run(['git', 'pull'])

    @staticmethod
    def __run_restart():
        # TODO implement
        pass

    @property
    def title(self) -> str:
        return 'SYS'

    def draw(self, image: Image, partial=False) -> (Image, int, int):
        width, height = config.RESOLUTION
        font = config.FONT_STANDARD

        left_top = (config.APP_SIDE_OFFSET, config.APP_TOP_OFFSET)
        draw = ImageDraw.Draw(image)

        if self.__result is not None:
            print(self.__result.stdout)
            print(self.__result.returncode)
            self.__result = None

        cursor = left_top
        for index, option in enumerate(self.__options):
            if index == self.__selected_index:
                draw.rectangle(cursor + (width / 2, cursor[1] + self.LINE_HEIGHT), fill=config.ACCENT_DARK)
            else:
                draw.rectangle(cursor + (width / 2, cursor[1] + self.LINE_HEIGHT), fill=config.BACKGROUND)
            draw.text(cursor, option.name, fill=config.ACCENT, font=font)
            cursor = (cursor[0], cursor[1] + self.LINE_HEIGHT)
        draw.line((width / 2, left_top[1]) + (width / 2, cursor[1]), fill=config.ACCENT, width=2)

        if partial:
            right_bottom = (width / 2, cursor[1])
            return image.crop(left_top + right_bottom), *left_top
        else:
            return image, 0, 0

    def on_key_left(self):
        pass

    def on_key_right(self):
        pass

    def on_key_up(self):
        self.__selected_index = (self.__selected_index - 1) % len(self.__options)

    def on_key_down(self):
        self.__selected_index = (self.__selected_index + 1) % len(self.__options)

    def on_key_a(self):
        self.__result = self.__options[self.__selected_index].action()

    def on_key_b(self):
        pass

    def on_app_enter(self):
        pass

    def on_app_leave(self):
        pass
