from app.App import App
from PIL import Image, ImageDraw
from subprocess import run, CompletedProcess, PIPE
from typing import Callable, Optional
import config


class UpdateApp(App):
    LINE_HEIGHT = 20
    CENTER_OFFSET = 10

    class Option:

        def __init__(self, name: str, action: Callable[[], Optional[CompletedProcess]],
                     count_action: Callable[[], Optional[int]] = None):
            self.__name = name
            self.__action = action
            self.__count_action = count_action

        @property
        def name(self) -> str:
            return self.__name

        @property
        def action(self) -> Callable[[], Optional[CompletedProcess]]:
            return self.__action

        @property
        def count_action(self) -> Callable[[], Optional[int]]:
            return self.__count_action

    def __init__(self):
        self.__selected_index = 0
        self.__files_to_reset: Optional[int] = None
        self.__files_to_clean: Optional[int] = None

        def get_files_to_reset():
            return self.__files_to_reset

        def get_files_to_clean():
            return self.__files_to_clean

        self.__options = [
            self.Option('fetch updates', self.__run_fetch),
            self.Option('reset changes', self.__run_reset, count_action=get_files_to_reset),
            self.Option('clean files', self.__run_clean, count_action=get_files_to_clean),
            self.Option('install updates', self.__run_install),
            self.Option('restart', self.__run_restart)
        ]
        self.__result = None

    @staticmethod
    def __run_fetch() -> CompletedProcess:
        return run(['git', 'fetch'], stdout=PIPE)

    @staticmethod
    def __run_reset() -> CompletedProcess:
        return run(['git', 'reset', '--hard'], stdout=PIPE)

    @staticmethod
    def __run_clean() -> CompletedProcess:
        return run(['git', 'clean', '-fd'], stdout=PIPE)

    @staticmethod
    def __run_install() -> CompletedProcess:
        return run(['git', 'pull'], stdout=PIPE)

    @staticmethod
    def __run_restart() -> CompletedProcess:
        # TODO implement
        pass

    @staticmethod
    def __get_files_to_reset() -> Optional[int]:
        result = run(['git', 'diff', '--name-only'], stdout=PIPE)
        if result.returncode == 0:
            if result.stdout is None:
                return 0
            else:
                return result.stdout.decode('utf-8').count('\n')
        else:
            return None

    @staticmethod
    def __get_files_to_clean() -> Optional[int]:
        result = run(['git', 'clean', '-nd'], stdout=PIPE)
        if result.returncode == 0:
            if result.stdout is None:
                return 0
            else:
                return result.stdout.decode('utf-8').count('\n')
        else:
            return None

    def __update_files_to_reset_and_clean(self):
        self.__files_to_reset = self.__get_files_to_reset()
        self.__files_to_clean = self.__get_files_to_clean()

    @property
    def title(self) -> str:
        return 'SYS'

    def draw(self, image: Image, partial=False) -> (Image, int, int):
        width, height = config.RESOLUTION
        font = config.FONT_STANDARD

        left_top = (config.APP_SIDE_OFFSET, config.APP_TOP_OFFSET)
        right_bottom = (width / 2, config.APP_TOP_OFFSET)
        draw = ImageDraw.Draw(image)

        if self.__result is not None:
            # log action responses
            print(f'code: {self.__result.returncode}')
            if self.__result.stdout:
                print(self.__result.stdout.decode('utf-8').rstrip('\n'))

            text = self.__result.stdout.decode('utf-8') if self.__result.stdout else f'code: {self.__result.returncode}'
            _, _, _, text_height = font.getbbox(text)
            log_left_top = (width / 2 + self.CENTER_OFFSET, left_top[1])
            right_bottom = (width - config.APP_SIDE_OFFSET, left_top[1] + text_height)
            draw.rectangle(log_left_top + right_bottom, fill=config.BACKGROUND)
            draw.text(log_left_top, text, fill=config.ACCENT, font=font)
            self.__result = None

        cursor = left_top
        for index, option in enumerate(self.__options):
            if index == self.__selected_index:
                draw.rectangle(cursor + (width / 2, cursor[1] + self.LINE_HEIGHT), fill=config.ACCENT_DARK)
            else:
                draw.rectangle(cursor + (width / 2, cursor[1] + self.LINE_HEIGHT), fill=config.BACKGROUND)
            text = option.name
            if option.count_action is not None:
                count = option.count_action()
                if count is not None:
                    text = f'{text} ({count} files)'
                else:
                    text = f'{text} (error)'
            draw.text(cursor, text, fill=config.ACCENT, font=font)
            cursor = (cursor[0], cursor[1] + self.LINE_HEIGHT)
            right_bottom = (max(right_bottom[0], width / 2), max(right_bottom[1], cursor[1]))
        draw.line((width / 2, left_top[1]) + (width / 2, cursor[1]), fill=config.ACCENT, width=1)

        if partial:
            # right_bottom = (width / 2, cursor[1])
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
        self.__update_files_to_reset_and_clean()

    def on_key_b(self):
        pass

    def on_app_enter(self):
        self.__update_files_to_reset_and_clean()

    def on_app_leave(self):
        pass
