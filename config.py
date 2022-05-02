from typing import List
from app.BaseApp import BaseApp
from app.FileManagerApp import FileManagerApp
from app.NullApp import NullApp
from interface.BaseInterface import BaseInterface
from interface.PillowInterface import PillowInterface
from interface.TkInterface import TkInterface


# General definition
# INTERFACE: BaseInterface = PillowInterface()
INTERFACE: BaseInterface = TkInterface()
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
