from dataclasses import dataclass, field

import yaml
from PIL import ImageFont
from yaml import Dumper, FullLoader, Loader, MappingNode, Node, UnsafeLoader


@dataclass
class SPIConfig:
    bus: int
    device: int


@dataclass
class I2CConfig:
    port: int
    address: int


@dataclass
class SerialConfig:
    port: str
    baud_rate: int


@dataclass
class ColorConfig:
    background: tuple[int, int, int]
    accent: tuple[int, int, int]
    accent_dark: tuple[int, int, int]


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
    modes: list[ColorConfig] = None
    # cached properties
    __font_header: ImageFont.FreeTypeFont | None = None
    __font_standard: ImageFont.FreeTypeFont | None = None

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
    def resolution(self) -> tuple[int, int]:
        return self.width, self.height

    @property
    def app_size(self) -> tuple[int, int]:
        return self.width - 2 * self.app_side_offset, self.height - self.app_top_offset - self.app_bottom_offset

    @property
    def font_header(self) -> ImageFont.FreeTypeFont:
        if self.__font_header is None:
            self.__font_header = ImageFont.truetype(self.font_name, self.font_header_size)
        return self.__font_header

    @property
    def font_standard(self) -> ImageFont.FreeTypeFont:
        if self.__font_standard is None:
            self.__font_standard = ImageFont.truetype(self.font_name, self.font_standard_size)
        return self.__font_standard

    @property
    def background(self) -> tuple[int, int, int]:
        return self.modes[self.color_mode].background

    @property
    def accent(self) -> tuple[int, int, int]:
        return self.modes[self.color_mode].accent

    @property
    def accent_dark(self) -> tuple[int, int, int]:
        return self.modes[self.color_mode].accent_dark


@dataclass
class KeypadConfig:
    # Buttons
    up_pin: int = 5
    down_pin: int = 6
    left_pin: int = 12
    right_pin: int = 13
    a_pin: int = 16
    b_pin: int = 26


@dataclass
class RotaryConfig:
    # Rotary encoder
    rotary_device: str = '/dev/input/event0'
    clk_pin: int = 22
    dt_pin: int = 23
    sw_pin: int = 27


@dataclass
class DisplayConfig:
    # Display module
    rst_pin: int = 25
    dc_pin: int = 24
    display_device: SPIConfig = field(default_factory=lambda: SPIConfig(0, 0))
    flip_display: bool = False

    # Touch module
    cs_pin: int = 7
    irq_pin: int = 17
    touch_device: SPIConfig = field(default_factory=lambda: SPIConfig(0, 1))


@dataclass
class Environment:
    dev_mode: bool = False
    env_sensor_config: I2CConfig = field(default_factory=lambda: I2CConfig(1, 0x76))
    adc_config: I2CConfig = field(default_factory=lambda: I2CConfig(1, 0x48))
    gps_module_config: SerialConfig = field(default_factory=lambda: SerialConfig('/dev/serial0', 9600))
    app_config: AppConfig = field(default_factory=lambda: AppConfig())
    keypad_config: KeypadConfig = field(default_factory=lambda: KeypadConfig())
    rotary_config: RotaryConfig = field(default_factory=lambda: RotaryConfig())
    display_config: DisplayConfig = field(default_factory=lambda: DisplayConfig())

    # cached property
    __is_raspberry_pi: bool | None = None

    @property
    def is_raspberry_pi(self):
        if self.__is_raspberry_pi is None:
            try:
                with open('/sys/firmware/devicetree/base/model', 'r') as model_info:
                    self.__is_raspberry_pi =  'Raspberry Pi' in model_info.read()
            except FileNotFoundError:
                self.__is_raspberry_pi = False
        return self.__is_raspberry_pi

def spi_config_constructor(loader: Loader | FullLoader | UnsafeLoader, node: Node) -> SPIConfig:
    if isinstance(node, MappingNode):
        values = loader.construct_mapping(node)
        return SPIConfig(**values)
    raise TypeError("node is not of type MappingNode")


def spi_config_representor(dumper: Dumper, data: SPIConfig) -> MappingNode:
    return dumper.represent_mapping('!SPIConfig', {k: v for k,v in vars(data).items() if k[0] != '_'})


def i2c_config_constructor(loader: Loader | FullLoader | UnsafeLoader, node: Node) -> I2CConfig:
    if isinstance(node, MappingNode):
        values = loader.construct_mapping(node)
        return I2CConfig(**values)
    raise TypeError("node is not of type MappingNode")


def i2c_config_representor(dumper: Dumper, data: I2CConfig) -> MappingNode:
    return dumper.represent_mapping('!I2CConfig', {k: v for k,v in vars(data).items() if k[0] != '_'})


def serial_config_constructor(loader: Loader | FullLoader | UnsafeLoader, node: Node) -> SerialConfig:
    if isinstance(node, MappingNode):
        values = loader.construct_mapping(node)
        return SerialConfig(**values)
    raise TypeError("node if not of type MappingNode")


def serial_config_representor(dumper: Dumper, data: SerialConfig) -> MappingNode:
    return dumper.represent_mapping('!SerialConfig', {k: v for k,v in vars(data).items() if k[0] != '_'})


def color_config_constructor(loader: Loader | FullLoader | UnsafeLoader, node: Node) -> ColorConfig:
    if isinstance(node, MappingNode):
        values = loader.construct_mapping(node)
        return ColorConfig(**values)
    raise TypeError("node is not of type MappingNode")


def color_config_representor(dumper: Dumper, data: ColorConfig) -> MappingNode:
    return dumper.represent_mapping('!ColorConfig', {k: v for k,v in vars(data).items() if k[0] != '_'})


def app_config_constructor(loader: Loader | FullLoader | UnsafeLoader, node: Node) -> AppConfig:
    if isinstance(node, MappingNode):
        values = loader.construct_mapping(node)
        return AppConfig(**values)
    raise TypeError("node is not of type MappingNode")


def app_config_representor(dumper: Dumper, data: AppConfig) -> MappingNode:
    return dumper.represent_mapping('!AppConfig', {k: v for k,v in vars(data).items() if k[0] != '_'})


def keypad_config_constructor(loader: Loader | FullLoader | UnsafeLoader, node: Node) -> KeypadConfig:
    if isinstance(node, MappingNode):
        values = loader.construct_mapping(node)
        return KeypadConfig(**values)
    raise TypeError("node is not of type MappingNode")


def keypad_config_representor(dumper: Dumper, data: KeypadConfig) -> MappingNode:
    return dumper.represent_mapping('!KeypadConfig', {k: v for k,v in vars(data).items() if k[0] != '_'})


def rotary_config_constructor(loader: Loader | FullLoader | UnsafeLoader, node: Node) -> RotaryConfig:
    if isinstance(node, MappingNode):
        values = loader.construct_mapping(node)
        return RotaryConfig(**values)
    raise TypeError("node is not of type MappingNode")


def rotary_config_representor(dumper: Dumper, data: RotaryConfig) -> MappingNode:
    return dumper.represent_mapping('!RotaryConfig', {k: v for k,v in vars(data).items() if k[0] != '_'})


def display_config_constructor(loader: Loader | FullLoader | UnsafeLoader, node: Node) -> DisplayConfig:
    if isinstance(node, MappingNode):
        values = loader.construct_mapping(node)
        return DisplayConfig(**values)
    raise TypeError("node is not of type MappingNode")


def display_config_representor(dumper: Dumper, data: DisplayConfig) -> MappingNode:
    return dumper.represent_mapping('!DisplayConfig', {k: v for k,v in vars(data).items() if k[0] != '_'})


def environment_constructor(loader: Loader | FullLoader | UnsafeLoader, node: Node) -> Environment:
    if isinstance(node, MappingNode):
        values = loader.construct_mapping(node)
        return Environment(**values)
    raise TypeError("node is not of type MappingNode")


def environment_representor(dumper: Dumper, data: Environment) -> MappingNode:
    return dumper.represent_mapping('!Environment', {k: v for k,v in vars(data).items() if k[0] != '_'})


def configure():
    yaml.add_constructor('!SPIConfig', spi_config_constructor)
    yaml.add_constructor('!I2CConfig', i2c_config_constructor)
    yaml.add_constructor('!SerialConfig', serial_config_constructor)
    yaml.add_constructor('!ColorConfig', color_config_constructor)
    yaml.add_constructor('!AppConfig', app_config_constructor)
    yaml.add_constructor('!KeypadConfig', keypad_config_constructor)
    yaml.add_constructor('!RotaryConfig', rotary_config_constructor)
    yaml.add_constructor('!DisplayConfig', display_config_constructor)
    yaml.add_constructor('!Environment', environment_constructor)
    yaml.add_representer(SPIConfig, spi_config_representor)
    yaml.add_representer(I2CConfig, i2c_config_representor)
    yaml.add_representer(SerialConfig, serial_config_representor)
    yaml.add_representer(ColorConfig, color_config_representor)
    yaml.add_representer(AppConfig, app_config_representor)
    yaml.add_representer(KeypadConfig, keypad_config_representor)
    yaml.add_representer(RotaryConfig, rotary_config_representor)
    yaml.add_representer(DisplayConfig, display_config_representor)
    yaml.add_representer(Environment, environment_representor)


def load(file_name: str = 'config.yaml') -> Environment:
    with open(file_name, 'r') as file:
        return yaml.load(file, FullLoader)


def save(environment: Environment, file_name: str = 'config.yaml'):
    with open(file_name, 'w') as file:
        yaml.dump(environment, file, sort_keys=False)
