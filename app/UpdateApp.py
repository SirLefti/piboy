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
                     result_text_action: Callable[[CompletedProcess], str],
                     count_action: Callable[[], Optional[int]] = None):
            self.__name = name
            self.__action = action
            self.__result_text_action = result_text_action
            self.__count_action = count_action

        @property
        def name(self) -> str:
            return self.__name

        @property
        def action(self) -> Callable[[], Optional[CompletedProcess]]:
            return self.__action

        @property
        def result_text_action(self) -> Callable[[CompletedProcess], str]:
            return self.__result_text_action

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

        def result_text_fetch(result: CompletedProcess) -> str:
            if result.returncode != 0:
                return 'error fetching updates'
            if not result.stdout.decode('utf-8'):
                return 'no updates available'
            return 'fetched updates, install next'

        def result_text_reset(result: CompletedProcess) -> str:
            if result.returncode != 0:
                return 'error resetting changes'
            if not result.stdout.decode('utf-8'):
                return 'no changes to reset'
            return 'reset changes'

        def result_text_clean(result: CompletedProcess) -> str:
            if result.returncode != 0:
                return 'error cleaning files'
            if not result.stdout.decode('utf-8'):
                return 'no files to clean'
            return 'cleaned files'

        def result_text_install(result: CompletedProcess) -> str:
            if result.returncode != 0:
                return 'error installing updates'
            if result.stdout.decode('utf-8').rstrip('\n') == 'Already up to date.':
                return 'no updates to install'
            return 'updates installed, restart next'

        def result_text_restart(result: CompletedProcess) -> str:
            if result.returncode != 0:
                return 'error restarting'
            return 'restarting...'

        self.__options = [
            self.Option('reset changes', self.__run_reset, result_text_reset, count_action=get_files_to_reset),
            self.Option('clean files', self.__run_clean, result_text_clean, count_action=get_files_to_clean),
            self.Option('fetch updates', self.__run_fetch, result_text_fetch),
            self.Option('install updates', self.__run_install, result_text_install),
            self.Option('restart', self.__run_restart, result_text_restart)
        ]
        self.__result = None
        self.__results = []

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
        return run(['sudo', 'reboot', 'now'], stdout=PIPE)

    @staticmethod
    def __get_files_to_reset() -> Optional[int]:
        result = run(['git', 'diff', '--name-only'], stdout=PIPE)
        if result.returncode != 0:
            return None
        if result.stdout is not None:
            return result.stdout.decode('utf-8').count('\n')
        return 0

    @staticmethod
    def __get_files_to_clean() -> Optional[int]:
        result = run(['git', 'clean', '-nd'], stdout=PIPE)
        if result.returncode != 0:
            return None
        if result.stdout is not None:
            return result.stdout.decode('utf-8').count('\n')
        return 0

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

        if self.__result is not None or not partial:
            # log action responses
            if self.__result is not None and self.__result.stdout:
                print(self.__result.stdout.decode('utf-8').rstrip('\n'))
            self.__result = None

            # clear existing logs
            cursor = (width / 2 + self.CENTER_OFFSET, left_top[1])
            rect_right_bottom = (cursor[1] +
                                 min(len(self.__results) * self.LINE_HEIGHT, height - config.APP_BOTTOM_OFFSET),
                                 width - config.APP_SIDE_OFFSET)
            draw.rectangle(cursor + rect_right_bottom, fill=config.BACKGROUND)
            # and draw history in reverse order
            for text in reversed(self.__results):
                _, _, _, text_height = font.getbbox(text)
                if cursor[1] + text_height > height - config.APP_BOTTOM_OFFSET:
                    break
                draw.text(cursor, text, fill=config.ACCENT, font=font)
                cursor = (cursor[0], cursor[1] + self.LINE_HEIGHT)
            right_bottom = (width - config.APP_SIDE_OFFSET, cursor[1])

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
        option = self.__options[self.__selected_index]
        result = option.action()
        self.__result = result
        self.__results.append(option.result_text_action(result))
        self.__update_files_to_reset_and_clean()

    def on_key_b(self):
        pass

    def on_app_enter(self):
        self.__update_files_to_reset_and_clean()

    def on_app_leave(self):
        pass
