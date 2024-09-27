import sys
import threading
from subprocess import CompletedProcess, run
from typing import Callable, Optional

from injector import inject
from PIL import Image, ImageDraw

from app.App import App
from core.decorator import override
from environment import AppConfig


class UpdateApp(App):
    LINE_HEIGHT = 20
    CENTER_OFFSET = 10

    class Option:

        def __init__(self, name: str,
                     actions: list[tuple[Callable[[], CompletedProcess[str]], Callable[[CompletedProcess[str]], str]]],
                     count_action: Optional[Callable[[], Optional[int]]] = None, count_name: Optional[str] = None):
            self.__name = name
            self.__actions = actions
            self.__count_action = count_action
            self.__count_name = count_name

        @property
        def name(self) -> str:
            return self.__name

        @property
        def actions(self) -> list[tuple[Callable[[], CompletedProcess[str]], Callable[[CompletedProcess[str]], str]]]:
            return self.__actions

        @property
        def count_action(self) -> Optional[Callable[[], Optional[int]]]:
            return self.__count_action

        @property
        def count_name(self) -> Optional[str]:
            return self.__count_name

    @inject
    def __init__(self, draw_callback: Callable[[bool], None], app_config: AppConfig):
        self.__draw_callback = draw_callback
        self.__resolution = app_config.resolution
        self.__background = app_config.background
        self.__color = app_config.accent
        self.__color_dark = app_config.accent_dark
        self.__app_top_offset = app_config.app_top_offset
        self.__app_side_offset = app_config.app_side_offset
        self.__app_bottom_offset = app_config.app_bottom_offset
        self.__font = app_config.font_standard

        self.__action_pending = False
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

        def result_text_fetch(result: CompletedProcess[str]) -> str:
            if result.returncode != 0:
                return 'error fetching updates'
            if not result.stdout:
                return 'no updates available'
            return 'fetched updates, install next'

        def result_text_reset(result: CompletedProcess[str]) -> str:
            if result.returncode != 0:
                return 'error resetting changes'
            if not result.stdout:
                return 'no changes to reset'
            return 'reset changes'

        def result_text_clean(result: CompletedProcess[str]) -> str:
            if result.returncode != 0:
                return 'error cleaning files'
            if not result.stdout:
                return 'no files to clean'
            return 'cleaned files'

        def result_text_install(result: CompletedProcess[str]) -> str:
            if result.returncode != 0:
                return 'error installing updates'
            if result.stdout.count('\n') == 1:
                # has only one line break at the end if the message is 'already up to date', but more when updating
                return 'no updates to install'
            return 'updates installed, restart next'

        def result_text_install_dependencies(result: CompletedProcess[str]) -> str:
            if result.returncode != 0:
                return 'error installing lib updates'
            if result.stdout.count('Successfully installed') == 0:
                return 'no lib updates to install'
            return 'lib updates installed, restart next'

        def result_text_shutdown(result: CompletedProcess[str]) -> str:
            if result.returncode != 0:
                return 'error shutting down'
            else:
                return 'shutting down...'

        def result_text_restart(result: CompletedProcess[str]) -> str:
            if result.returncode != 0:
                return 'error restarting'
            return 'restarting...'

        self.__options = [
            self.Option('reset changes',[(self.__run_reset, result_text_reset)],
                        count_action=get_files_to_reset, count_name='files'),
            self.Option('clean files', [(self.__run_clean, result_text_clean)],
                        count_action=get_files_to_clean, count_name='files'),
            self.Option('fetch updates', [(self.__run_fetch, result_text_fetch)]),
            self.Option('install updates', [
                (self.__run_install, result_text_install),
                (self.__run_install_dependencies, result_text_install_dependencies)
            ], count_action=get_commits_to_update, count_name='commits'),
            self.Option('shutdown', [(self.__run_shutdown, result_text_shutdown)]),
            self.Option('restart', [(self.__run_restart, result_text_restart)])
        ]
        self.__results: list[str] = []
        self.__last_results_length = len(self.__results)

    @staticmethod
    def __run_fetch() -> CompletedProcess[str]:
        # git fetch does not return stuff into stdout, return output of git log instead
        result = run(['git', 'fetch'], capture_output=True, text=True)
        if result.returncode != 0:
            return result
        return run(['git', 'log', '..@{u}', '--pretty=oneline'], capture_output=True, text=True)

    @staticmethod
    def __run_reset() -> CompletedProcess[str]:
        return run(['git', 'reset', '--hard'], capture_output=True, text=True)

    @staticmethod
    def __run_clean() -> CompletedProcess[str]:
        return run(['git', 'clean', '-fd'], capture_output=True, text=True)

    @staticmethod
    def __run_install() -> CompletedProcess[str]:
        return run(['git', 'pull'], capture_output=True, text=True)

    @staticmethod
    def __run_install_dependencies() -> CompletedProcess[str]:
        return run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements-pi.txt'], capture_output=True, text=True)

    @staticmethod
    def __run_shutdown() -> CompletedProcess[str]:
        return run(['sudo', 'shutdown', 'now'], text=True)

    @staticmethod
    def __run_restart() -> CompletedProcess[str]:
        return run(['sudo', 'reboot', 'now'], text=True)

    @staticmethod
    def __get_files_to_reset() -> Optional[int]:
        result = run(['git', 'diff', '--name-only'], capture_output=True, text=True)
        if result.returncode != 0:
            return None
        if result.stdout is not None:
            return result.stdout.count('\n')
        return 0

    @staticmethod
    def __get_files_to_clean() -> Optional[int]:
        result = run(['git', 'clean', '-nd'], capture_output=True, text=True)
        if result.returncode != 0:
            return None
        if result.stdout is not None:
            return result.stdout.count('\n')
        return 0

    @staticmethod
    def __get_commits_to_update() -> Optional[int]:
        result = run(['git', 'rev-list', '@{upstream}', '--not', 'HEAD'], capture_output=True, text=True)
        if result.returncode != 0:
            return None
        if result.stdout is not None:
            return result.stdout.count('\n')
        return 0

    @staticmethod
    def __get_branch_name() -> Optional[str]:
        result = run(['git', 'branch', '--show-current'], capture_output=True, text=True)
        if result.returncode != 0:
            return None
        if result.stdout is not None:
            return result.stdout
        return None

    @staticmethod
    def __get_remote_name() -> Optional[str]:
        result = run(['git', 'remote', 'show'], capture_output=True, text=True)
        if result.returncode != 0:
            return None
        if result.stdout is not None:
            return result.stdout
        return None

    def __update_counts(self):
        self.__files_to_reset = self.__get_files_to_reset()
        self.__files_to_clean = self.__get_files_to_clean()
        self.__commits_to_update = self.__get_commits_to_update()

    @property
    @override
    def title(self) -> str:
        return 'SYS'

    @override
    def draw(self, image: Image.Image, partial=False) -> tuple[Image.Image, int, int]:
        width, height = self.__resolution
        font = self.__font

        left_top = (self.__app_side_offset, self.__app_top_offset)
        right_bottom = (width // 2, self.__app_top_offset)
        draw = ImageDraw.Draw(image)

        # part: result history
        if self.__last_results_length != len(self.__results) or not partial:
            self.__last_results_length = len(self.__results)

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

    @override
    def on_key_up(self):
        self.__selected_index = (self.__selected_index - 1) % len(self.__options)

    @override
    def on_key_down(self):
        self.__selected_index = (self.__selected_index + 1) % len(self.__options)

    @override
    def on_key_a(self):
        if self.__action_pending:
            self.__results.append('action pending')
            self.__draw_callback(True)
        else:
            def process_all():
                option = self.__options[self.__selected_index]
                self.__action_pending = True
                for action, result_text_action in option.actions:
                    result = action()
                    # Log complete output
                    print(result.stdout.rstrip('\n'))
                    self.__results.append(result_text_action(result))
                    self.__update_counts()
                    self.__draw_callback(True)
                self.__action_pending = False

            thread = threading.Thread(target=process_all, args=(), daemon=True)
            thread.start()


    @override
    def on_app_enter(self):
        self.__update_counts()
