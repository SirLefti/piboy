from app.App import App
from PIL import Image, ImageDraw, ImageFont
from subprocess import run, CompletedProcess, PIPE
from typing import Callable, Optional


class UpdateApp(App):
    LINE_HEIGHT = 20
    CENTER_OFFSET = 10

    class Option:

        def __init__(self, name: str, action: Callable[[], CompletedProcess],
                     result_text_action: Callable[[CompletedProcess], str],
                     count_action: Optional[Callable[[], Optional[int]]] = None,
                     count_name: Optional[str] = None):
            self.__name = name
            self.__action = action
            self.__result_text_action = result_text_action
            self.__count_action = count_action
            self.__count_name = count_name

        @property
        def name(self) -> str:
            return self.__name

        @property
        def action(self) -> Callable[[], CompletedProcess]:
            return self.__action

        @property
        def result_text_action(self) -> Callable[[CompletedProcess], str]:
            return self.__result_text_action

        @property
        def count_action(self) -> Optional[Callable[[], Optional[int]]]:
            return self.__count_action

        @property
        def count_name(self) -> Optional[str]:
            return self.__count_name

    def __init__(self, resolution: tuple[int, int],
                 background: tuple[int, int, int], color: tuple[int, int, int], color_dark: tuple[int, int, int],
                 app_top_offset: int, app_side_offset: int, app_bottom_offset: int,
                 font_standard: ImageFont.FreeTypeFont):
        self.__resolution = resolution
        self.__background = background
        self.__color = color
        self.__color_dark = color_dark
        self.__app_top_offset = app_top_offset
        self.__app_side_offset = app_side_offset
        self.__app_bottom_offset = app_bottom_offset
        self.__font = font_standard

        self.__selected_index = 0
        self.__files_to_reset: Optional[int] = None
        self.__files_to_clean: Optional[int] = None
        self.__commits_to_update: Optional[int] = None
        self.__branch_name = self.__get_branch_name()
        self.__remote_name = self.__get_remote_name()

        def get_files_to_reset() -> Optional[int]:
            return self.__files_to_reset

        def get_files_to_clean() -> Optional[int]:
            return self.__files_to_clean

        def get_commits_to_update() -> Optional[int]:
            return self.__commits_to_update

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

        def result_text_shutdown(result: CompletedProcess) -> str:
            if result.returncode != 0:
                return 'error shutting down'
            else:
                return 'shutting down...'

        def result_text_restart(result: CompletedProcess) -> str:
            if result.returncode != 0:
                return 'error restarting'
            return 'restarting...'

        self.__options = [
            self.Option('reset changes', self.__run_reset, result_text_reset,
                        count_action=get_files_to_reset, count_name='files'),
            self.Option('clean files', self.__run_clean, result_text_clean,
                        count_action=get_files_to_clean, count_name='files'),
            self.Option('fetch updates', self.__run_fetch, result_text_fetch),
            self.Option('install updates', self.__run_install, result_text_install,
                        count_action=get_commits_to_update, count_name='commits'),
            self.Option('shutdown', self.__run_shutdown, result_text_shutdown),
            self.Option('restart', self.__run_restart, result_text_restart)
        ]
        self.__result: Optional[CompletedProcess] = None
        self.__results: list[str] = []

    @staticmethod
    def __run_fetch() -> CompletedProcess:
        # git fetch does not return stuff into stdout, return output of git log instead
        result = run(['git', 'fetch'], stdout=PIPE)
        if result.returncode != 0:
            return result
        return run(['git', 'log', '..@{u}', '--pretty=oneline'], stdout=PIPE)

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
    def __run_shutdown() -> CompletedProcess:
        return run(['sudo', 'shutdown', 'now'], stdout=PIPE)

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

    @staticmethod
    def __get_commits_to_update() -> Optional[int]:
        result = run(['git', 'rev-list', '@{upstream}', '--not', 'HEAD'], stdout=PIPE)
        if result.returncode != 0:
            return None
        if result.stdout is not None:
            return result.stdout.decode('utf-8').count('\n')
        return 0

    @staticmethod
    def __get_branch_name() -> Optional[str]:
        result = run(['git', 'branch', '--show-current'], stdout=PIPE)
        if result.returncode != 0:
            return None
        if result.stdout is not None:
            return result.stdout.decode('utf-8')
        return None

    @staticmethod
    def __get_remote_name() -> Optional[str]:
        result = run(['git', 'remote', 'show'], stdout=PIPE)
        if result.returncode != 0:
            return None
        if result.stdout is not None:
            return result.stdout.decode('utf-8')
        return None

    def __update_counts(self):
        self.__files_to_reset = self.__get_files_to_reset()
        self.__files_to_clean = self.__get_files_to_clean()
        self.__commits_to_update = self.__get_commits_to_update()

    @property
    def title(self) -> str:
        return 'SYS'

    def draw(self, image: Image.Image, partial=False) -> tuple[Image.Image, int, int]:
        width, height = self.__resolution
        font = self.__font

        left_top = (self.__app_side_offset, self.__app_top_offset)
        right_bottom = (width // 2, self.__app_top_offset)
        draw = ImageDraw.Draw(image)

        # part: result history
        if self.__result is not None or not partial:
            # log action responses
            if self.__result is not None and self.__result.stdout:
                print(self.__result.stdout.decode('utf-8').rstrip('\n'))
            self.__result = None

            # clear existing logs
            history_cursor: tuple[int, int] = (width // 2 + self.CENTER_OFFSET, left_top[1])
            rect_right_bottom = (width - self.__app_side_offset,
                                 history_cursor[1] +
                                 min(len(self.__results) * self.LINE_HEIGHT, height - self.__app_bottom_offset))
            draw.rectangle(history_cursor + rect_right_bottom, fill=self.__background)
            # and draw history in reverse order
            for text in reversed(self.__results):
                _, _, _, text_height = font.getbbox(text)
                if history_cursor[1] + text_height > height - self.__app_bottom_offset:
                    break
                draw.text(history_cursor, text, fill=self.__color, font=font)
                history_cursor = (history_cursor[0], history_cursor[1] + self.LINE_HEIGHT)
            right_bottom = (width - self.__app_side_offset, history_cursor[1])

        # part: options
        cursor: tuple[int, int] = left_top
        for index, option in enumerate(self.__options):
            if index == self.__selected_index:
                draw.rectangle(cursor + (width // 2, cursor[1] + self.LINE_HEIGHT), fill=self.__color_dark)
            else:
                draw.rectangle(cursor + (width // 2, cursor[1] + self.LINE_HEIGHT), fill=self.__background)
            text = option.name
            if option.count_action is not None and option.count_name:
                count = option.count_action()
                if count is not None:
                    text = f'{text} ({count} {option.count_name})'
                else:
                    text = f'{text} (error)'
            draw.text(cursor, text, fill=self.__color, font=font)
            cursor = (cursor[0], cursor[1] + self.LINE_HEIGHT)
            right_bottom = (max(right_bottom[0], width // 2), max(right_bottom[1], cursor[1]))
        draw.line((width // 2, left_top[1]) + (width // 2, cursor[1]), fill=self.__color, width=1)

        # part: repository and branch information
        if not partial:
            # information does not change, so just draw it initially
            unknown = 'unknown'
            _, _, _, text_height_branch = font.getbbox(self.__branch_name or unknown)
            _, _, _, text_height_remote = font.getbbox(self.__remote_name or unknown)
            draw.text((self.__app_side_offset, height - self.__app_bottom_offset - text_height_branch -
                       text_height_remote), f'branch: {self.__branch_name or unknown}', fill=self.__color, font=font)
            draw.text((self.__app_side_offset, height - self.__app_bottom_offset - text_height_remote),
                      f'remote: {self.__remote_name or unknown}', fill=self.__color, font=font)

        if partial:
            return image.crop(left_top + right_bottom), *left_top  # noqa (unpacking type check fail)
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
        self.__update_counts()

    def on_key_b(self):
        pass

    def on_app_enter(self):
        self.__update_counts()

    def on_app_leave(self):
        pass
