import time
import wave
from enum import Enum
from multiprocessing import Process
from multiprocessing.connection import Connection, Pipe  # noqa just import Connection for typing
from threading import Thread
from typing import Callable

import pyaudio

from core.decorator import override


class Command(Enum):
    START = 1
    PAUSE = 2
    STOP = 3
    HAS_STREAM = 4
    IS_ACTIVE = 5
    PROGRESS = 6
    LOAD_FILE = 7
    CALLBACK_NEXT = 8


class AudioProcess(Process):

    def __init__(self, cmd_connection: Connection, cb_connection: Connection):
        """
        PyAudio wrapper running in a separate process to avoid audio issues when running into the global interpreter
        lock.
        :param cmd_connection: pipe connection to receive commands and send return values
        :param cb_connection: pipe connection to send callbacks
        """
        super().__init__()
        self.__cmd_connection = cmd_connection
        self.__cb_connection = cb_connection
        self.__player = pyaudio.PyAudio()
        self.__total_frames = 0
        self.__played_frames = 0
        self.__wave_read : wave.Wave_read | None = None
        self.__stream: pyaudio.Stream | None = None
        self.__is_continuing = False

    def __delayed_call_next(self, delay: float = 1):
        """
        Waits for the given delay and checks then, if the stream was paused or stopped in the meantime. If not, the
        callback is sent to proceed with the next file. If yes, the callback is not sent.
        :param delay: delay in seconds before sending the callback
        :return:
        """
        time.sleep(delay)
        # only call next if the playback was not stopped in the meantime, which is marked by __is_continuing
        if self.__is_continuing:
            self.__cb_connection.send(Command.CALLBACK_NEXT)

    def __stream_callback(self, _1, frame_count, _2, _3) -> tuple[bytes, int]:
        data = self.__wave_read.readframes(frame_count)
        self.__played_frames += frame_count
        if self.__played_frames >= self.__total_frames:
            thread_call_next = Thread(target=self.__delayed_call_next, args=(), daemon=True)
            thread_call_next.start()
            return bytes(), pyaudio.paComplete
        else:
            return data, pyaudio.paContinue

    def __load_file(self, file_path: str):
        """
        Loads the file from the given path and creates a stream for it. There is no validation, if the path and file are
        valid.
        :param file_path: path of the audio file
        :return:
        """
        self.__wave_read = wave.open(file_path, 'rb')
        self.__total_frames = self.__wave_read.getnframes()
        self.__played_frames = 0

        self.__stream = self.__player.open(format=self.__player.get_format_from_width(
            self.__wave_read.getsampwidth()),
            channels=self.__wave_read.getnchannels(),
            rate=self.__wave_read.getframerate(),
            output=True,
            stream_callback=self.__stream_callback)

    def __start_stream(self) -> bool:
        """
        Starts the current audio stream if available.
        :return: `True` is the stream was started, else `False`
        """
        if self.__stream:
            self.__stream.start_stream()
            self.__is_continuing = True
            return True
        return False

    def __pause_stream(self) -> bool:
        """
        Pauses the current audio stream if available.
        :return: `True` if the stream was paused, else `False`
        """
        if self.__stream:
            self.__stream.stop_stream()
            self.__is_continuing = False
            return True
        return False

    def __stop_stream(self) -> bool:
        """
        Closes the current audio stream if available.
        :return: `True` if a stream was closed, else `False`
        """
        if self.__stream:
            self.__stream.stop_stream()
            self.__stream.close()
            self.__stream = None
            self.__is_continuing = False
            self.__total_frames = 0
            self.__played_frames = 0
            return True
        return False

    def __progress(self) -> float | None:
        """
        Calculates the progress from played and total frames.
        :return: progress as `float` between 0 and 1 if a valid file was loaded, else `None`
        """
        if self.__total_frames == 0:
            return None
        if self.__total_frames <= self.__played_frames:
            return 1
        return self.__played_frames / self.__total_frames

    @override
    def run(self):
        # for some very weird reason this is needed because pyaudio is not initialized when creating the process
        self.__player.__init__()
        while True:
            value = self.__cmd_connection.recv()
            option = None
            if isinstance(value, tuple) and len(value) == 2:
                value, option = value
            match value:
                case Command.START:
                    self.__cmd_connection.send(self.__start_stream())
                case Command.PAUSE:
                    self.__cmd_connection.send(self.__pause_stream())
                case Command.STOP:
                    self.__cmd_connection.send(self.__stop_stream())
                case Command.HAS_STREAM:
                    self.__cmd_connection.send(self.__stream is not None)
                case Command.IS_ACTIVE:
                    self.__cmd_connection.send(self.__stream is not None and self.__stream.is_active())
                case Command.PROGRESS:
                    self.__cmd_connection.send(self.__progress())
                case Command.LOAD_FILE:
                    self.__load_file(option)


    def __del__(self):
        if self.__stream is not None:
            self.__stream.close()
        self.__player.terminate()


class MultiprocessingAudioPlayer:

    def __init__(self, callback_next: Callable[[], None]):
        """
        Audio player using PyAudio, that uses multiprocessing to run in a separate process to avoid limitations caused
        by the global interpreter lock.
        :param callback_next: callback to load and play the next file, will be called after the current file has ended
        """
        self.__callback_next = callback_next
        p_cmd_connection, c_cmd_connection = Pipe(duplex=True)
        p_cb_connection, c_cb_connection = Pipe(duplex=True)
        self.__cmd_connection = p_cmd_connection
        self.__cb_connection = p_cb_connection
        self.__process = AudioProcess(c_cmd_connection, c_cb_connection)
        self.__process.start()
        self.__thread = Thread(target=self.__callback_listener, args=(), daemon=True)
        self.__thread.start()

    def __callback_listener(self):
        while True:
            value = self.__cb_connection.recv()
            match value:
                case Command.CALLBACK_NEXT:
                    self.__callback_next()

    def __mp_cmd_bool(self, command: Command) -> bool:
        """
        Wrapper to send a command and collecting a return value.
        :param command: command to send
        :return: `True` if and only if the returned value was `True`, else `False`
        """
        self.__cmd_connection.send(command)
        if self.__cmd_connection.poll(timeout=1):  # do not wait forever for an answer
            value = self.__cmd_connection.recv()
            return value == True  # make sure to return definitely a bool
        return False

    def load_file(self, file_path: str):
        """
        Requests the audio process to load the file from given path. There is no validation, if the path and file are
        valid.
        :param file_path: path of the audio file
        :return:
        """
        self.__cmd_connection.send((Command.LOAD_FILE, file_path))

    def start_stream(self) -> bool:
        """
        Requests the audio process to start the stream if available.
        :return: `True` if the stream was started, else `False`
        """
        return self.__mp_cmd_bool(Command.START)

    def pause_stream(self) -> bool:
        """
        Requests the audio process to pause the stream if available.
        :return: `True` if the stream was paused, else `False`
        """
        return self.__mp_cmd_bool(Command.PAUSE)

    def stop_stream(self) -> bool:
        """
        Requests the audio process to stop the stream if available.
        :return: `True` if the stream was stopped, else `False`
        """
        return self.__mp_cmd_bool(Command.STOP)

    @property
    def has_stream(self) -> bool:
        """
        :return: `True` if a file is currently loaded, else `False`
        """
        return self.__mp_cmd_bool(Command.HAS_STREAM)

    @property
    def is_active(self) -> bool:
        """
        :return: `True` if a file is currently played, else `False`
        """
        return self.__mp_cmd_bool(Command.IS_ACTIVE)

    @property
    def progress(self) -> float | None:
        """
        :return: progress as `float` between 0 and 1 if a valid file was loaded, else `None`
        """
        self.__cmd_connection.send(Command.PROGRESS)
        if self.__cmd_connection.poll(timeout=1):  # do not wait forever for an answer
            value = self.__cmd_connection.recv()
            return value
        return None
