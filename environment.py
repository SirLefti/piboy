from dataclasses import dataclass
from typing import Tuple, List
from PIL import ImageFont
from yaml import Loader, Dumper, MappingNode, Node, FullLoader
import yaml


@dataclass
class SPIConfig:
    bus: int
    device: int


@dataclass
class ColorConfig:
    background: Tuple[int, int, int]
    accent: Tuple[int, int, int]
    accent_dark: Tuple[int, int, int]


@dataclass
class AppConfig:
    app_side_offset: int = 20
    app_top_offset: int = 30
    app_bottom_offset: int = 25
    font_name: str = 'FreeSansBold.ttf'
    font_header_size: int = 16
    font_standard_size: int = 14
    color_mode: int = 0
    width: int = 480
    height: int = 320
    modes: List[ColorConfig] = None

    def __post_init__(self):
        if self.modes is None:
            self.modes = [
                ColorConfig(
                    background=(0, 0, 0),
                    accent=(27, 251, 30),
                    accent_dark=(9, 64, 9)
                ),
                ColorConfig(
                    background=(0, 0, 0),
                    accent=(255, 245, 101),
                    accent_dark=(59, 45, 25)
                )
            ]

    @property
    def resolution(self) -> Tuple[int, int]:
        return self.width, self.height

    @property
    def font_header(self) -> ImageFont:
        return ImageFont.truetype(self.font_name, self.font_header_size)

    @property
    def font_standard(self) -> ImageFont:
        return ImageFont.truetype(self.font_name, self.font_standard_size)

    @property
    def background(self) -> Tuple[int, int, int]:
        return self.modes[self.color_mode].background

    @property
    def accent(self) -> Tuple[int, int, int]:
        return self.modes[self.color_mode].accent

    @property
    def accent_dark(self) -> Tuple[int, int, int]:
        return self.modes[self.color_mode].accent_dark


@dataclass
class PinConfig:
    # Buttons
    up_pin: int = 5
    down_pin: int = 6
    left_pin: int = 12
    right_pin: int = 13
    a_pin: int = 16
    b_pin: int = 26

    # Rotary encoder
    clk_pin: int = 22
    dt_pin: int = 23
    sw_pin: int = 27

    # Display module
    rst_pin: int = 25
    dc_pin: int = 24

    # Touch module
    cs_pin: int = 7
    irq_pin: int = 17


@dataclass
class Environment:
    dev_mode: bool = True
    flip_display: bool = False
    display_config: SPIConfig = SPIConfig(0, 0)
    touch_config: SPIConfig = SPIConfig(0, 1)
    app_config: AppConfig = AppConfig()
    pin_config: PinConfig = PinConfig()


def spi_config_constructor(loader: Loader, node: Node) -> SPIConfig:
    values = loader.construct_mapping(node)
    return SPIConfig(**values)


def spi_config_representor(dumper: Dumper, data: SPIConfig) -> MappingNode:
    return dumper.represent_mapping('!SPIConfig', vars(data))


def color_config_constructor(loader: Loader, node: Node) -> ColorConfig:
    values = loader.construct_mapping(node)
    return ColorConfig(**values)


def color_config_representor(dumper: Dumper, data: ColorConfig) -> MappingNode:
    return dumper.represent_mapping('!ColorConfig', vars(data))


def app_config_constructor(loader: Loader, node: Node) -> AppConfig:
    values = loader.construct_mapping(node)
    return AppConfig(**values)


def app_config_representor(dumper: Dumper, data: AppConfig) -> MappingNode:
    return dumper.represent_mapping('!AppConfig', vars(data))


def pin_config_constructor(loader: Loader, node: Node) -> PinConfig:
    values = loader.construct_mapping(node)
    return PinConfig(**values)


def pin_config_representor(dumper: Dumper, data: PinConfig) -> MappingNode:
    return dumper.represent_mapping('!PinConfig', vars(data))


def environment_constructor(loader: Loader, node: Node) -> Environment:
    values = loader.construct_mapping(node)
    return Environment(**values)


def environment_representor(dumper: Dumper, data: Environment) -> MappingNode:
    return dumper.represent_mapping('!Environment', vars(data))


def configure():
    yaml.add_constructor('!SPIConfig', spi_config_constructor)
    yaml.add_constructor('!ColorConfig', color_config_constructor)
    yaml.add_constructor('!AppConfig', app_config_constructor)
    yaml.add_constructor('!PinConfig', pin_config_constructor)
    yaml.add_constructor('!Environment', environment_constructor)
    yaml.add_representer(SPIConfig, spi_config_representor)
    yaml.add_representer(ColorConfig, color_config_representor)
    yaml.add_representer(AppConfig, app_config_representor)
    yaml.add_representer(PinConfig, pin_config_representor)
    yaml.add_representer(Environment, environment_representor)


def load(file_name: str = 'config.yaml') -> Environment:
    with open(file_name, 'r') as file:
        return yaml.load(file, FullLoader)


def save(environment: Environment, file_name: str = 'config.yaml'):
    with open(file_name, 'w') as file:
        yaml.dump(environment, file, sort_keys=False)
