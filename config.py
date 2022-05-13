import piboy
from typing import List, Callable
from app.BaseApp import BaseApp
from app.FileManagerApp import FileManagerApp
from app.NullApp import NullApp
from interface.BaseInterface import BaseInterface
from interface.BaseInput import BaseInput
from interface.PillowInterface import PillowInterface
from interface.TkInterface import TkInterface

# General definition
ON_KEY_LEFT: Callable = piboy.on_key_left
ON_KEY_UP: Callable = piboy.on_key_up
ON_KEY_RIGHT: Callable = piboy.on_key_right
ON_KEY_DOWN: Callable = piboy.on_key_down
ON_KEY_A: Callable = piboy.on_key_a
ON_KEY_B: Callable = piboy.on_key_b
ON_ROTARY_INCREASE: Callable = piboy.on_rotary_increase
ON_ROTARY_DECREASE: Callable = piboy.on_rotary_decrease

__tk = TkInterface()
# INTERFACE: BaseInterface = PillowInterface()
INTERFACE: BaseInterface = __tk
INPUT: BaseInput = __tk
FONT = 'FreeSansBold.ttf'
BACKGROUND = (0, 0, 0)
ACCENT = (27, 251, 30)
ACCENT_INACTIVE = (9, 64, 9)
# Pin definition
RST_PIN = 25
DC_PIN = 24
# SPI definition
SPI_BUS = 0
SPI_DEVICE = 0
# App definition
APPS: List[BaseApp] = [FileManagerApp(), NullApp('DATA'), NullApp('STATS'), NullApp('RADIO'), NullApp('MAP')]
