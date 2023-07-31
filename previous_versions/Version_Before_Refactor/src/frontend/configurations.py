import logging
from dataclasses import dataclass


class Config:
    button_width: int = 17
    small_button_width: int = 7
    text_entry_width: int = int(1.55 * button_width)
    button_height: int = 1
    bg_color: str = "#1C1C1C"

    def __post_init__(self):
        for key, value in self.__dict__.items():
            if not isinstance(value, type(self.__class__.__dict__[key])):
                logging.info(
                    f"Yaml-file value for {key} is of type {type(value)} instead of "
                    f"being of type {type(self.__class__.__dict__[key])}")
                self.__dict__[key] = self.__class__.__dict__[key]


@dataclass
class MainScreenConfig(Config):
    width: int = 420
    height: int = 690
    relative_open_on_startup: bool = True
    fuel_open_on_startup: bool = True


@dataclass
class SettingsScreenConfig(Config):
    width: int = 420
    height: int = 950
    block_width: int = 200
    block_height: int = 100
    checkbutton_width: int = 10


@dataclass
class LoginScreenConfig(Config):
    width: int = 420
    height: int = 690
    auto_login_activation: bool = False


@dataclass
class FuelScreenConfig(Config):
    font_size: int = 16
    font_style: str = "TkFixedFont"
    font_extra: str = "bold"
    text_padding: int = 5
    offset_right: int = 5
    offset_down: int = 5
    fg_color_header: str = "#0061B7"
    fg_color_values: str = "#EAEAEA"
    fg_color_special: str = "#E12D5C"
    fuel_activated: bool = True
    last_activated: bool = True
    avg_activated: bool = True
    target_activated: bool = True
    range_activated: bool = True
    refuel_activated: bool = True
    finish_activated: bool = True
    remaining_activated: bool = True
    safety_margin: float = 5


@dataclass
class RelativeScreenConfig(Config):
    font_size: int = 12
    text_padding_x: int = 3
    text_padding_y: int = 2
    offset_right: int = 1350
    offset_down: int = 850
    hide_pits: bool = False
    license_activated: bool = True
    irating_activated: bool = True
