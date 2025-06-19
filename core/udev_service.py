import logging
import os
import re
import threading
from os import path
from subprocess import PIPE, run

import pyudev

logger = logging.getLogger(__name__)

class UDevService:

    loop_thread = None

    def __init__(self, mount_root: str = path.join(path.expanduser('~'), 'media')):
        self._mount_root = mount_root
        self._context = pyudev.Context()
        self._monitor = pyudev.Monitor.from_netlink(self._context)
        self._monitor.filter_by('block', 'partition')

    def start(self):
        # make sure that the mount root exists
        try:
            os.mkdir(self._mount_root)
            logger.info('created mount root')
        except FileExistsError:
            pass
        self.loop_thread = threading.Thread(target=self._loop, daemon=True)
        self.loop_thread.start()

    def _loop(self):
        while True:
            device = self._monitor.poll()
            if device.action == 'add':
                self.mount(device)
            if device.action == 'remove':
                self.unmount(device)

    def _build_target_path(self, device_node: str, model: str) -> str:
        partition_number = next(iter(re.findall(r'/dev/\w+(\d)', device_node)), 0)
        return path.abspath(path.join(self._mount_root, f'{model}_{partition_number}'))

    def mount(self, device: pyudev.Device):
        model = device.properties['ID_MODEL']
        device_node = device.device_node
        target_path = self._build_target_path(device_node, model)

        try:
            os.mkdir(target_path)
            logger.info(f'created directory {target_path}')
        except FileExistsError:
            # this means the directory already exists, check if it is empty
            files = os.listdir(target_path)
            if files:
                logger.warning('target mount is not empty!')
                return

        result = run(['sudo', 'mount', device_node, target_path], stdout=PIPE)

        if result.returncode == 0:
            logger.info(f'mounted {device_node} at {target_path}')
        else:
            logger.error(f'unable to mount {device_node} at {target_path}: {result.returncode}')
            os.rmdir(target_path)

    def unmount(self, device):
        model = device.properties['ID_MODEL']
        device_node = device.device_node
        target_path = self._build_target_path(device_node, model)

        result = run(['sudo', 'umount', target_path], stdout=PIPE)

        if result.returncode == 0:
            logger.info(f'unmounted {device_node} at {target_path}')
        else:
            logger.error(f'unable to unmount {device_node} at {target_path}: {result.returncode}')

        try:
            os.rmdir(target_path)
            logger.info(f'removed directory {target_path}')
        except FileNotFoundError:
            logger.warning(f'did not remove directory {target_path} because it did not exist')

if __name__ == '__main__':
    service = UDevService()
    service.start()
