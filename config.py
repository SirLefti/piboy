from app.FileManagerApp import FileManagerApp
from interface.BaseInterface import BaseInterface
from interface.DevInterface import DevInterface
# General definition
INTERFACE: BaseInterface = DevInterface()
# Pin definition
RST_PIN = 25
DC_PIN = 24
# SPI definition
SPI_BUS = 0
SPI_DEVICE = 0
# App definition
APPS = {1: FileManagerApp()}
