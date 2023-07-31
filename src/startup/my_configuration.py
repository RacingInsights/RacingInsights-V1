"""Module for logging"""
import logging
from abc import ABC, abstractmethod

import yaml


class Config(ABC):
    """Configuration abstract base class"""
    button_width: int = 17
    small_button_width: int = 7
    text_entry_width: int = int(1.55 * button_width)
    button_height: int = 1
    bg: str = "#1C1C1C"

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Used to indicate that config classes should have a name attribute.
        Returns the name of the object.
        """


def add_entries_to_config(config_object: Config, **entries) -> None:
    """Adds the entries of the dict to the config object if valid"""
    valid_items = config_object.__dict__

    for key, value in entries.items():
        # Check if the given key is part of the configuration
        if key not in valid_items:
            logging.warning("Key '%s' is not valid", key)
            continue

        # Check if the given value is of the correct type
        if not isinstance(value, type(valid_items[f"{key}"])):
            logging.warning(
                    "The type for the value of key '%s' is not valid\n"
                    "             Expected: %s\n"
                    "             Received: %s",
                    key, type(valid_items[f'{key}']), type(value))
            continue

        # If key valid and value type correct, add it to the config object
        logging.info("Key '%s' and value %s are valid", key, value)
        entry = {f'{key}': value}
        config_object.__dict__.update(entry)


# OVERLAY CONFIGS
class OverlayConfig(Config):
    """Defines the minimal properties to be implemented by each overlay"""
    offset_down: int
    offset_right: int
    transparency: float
    name: str
    font_size: int
    text_padding: int


class FuelConfig(OverlayConfig):
    """Class containing all configuration settings for fuel overlay"""
    name = "fuel"

    def __init__(self, **entries):
        # Fuel specific configurations
        self.active: bool = True
        self.avg_activated: bool = True
        self.finish_activated: bool = True
        self.fuel_activated: bool = True
        self.last_activated: bool = True
        self.range_activated: bool = True
        self.refuel_activated: bool = True
        self.remaining_activated: bool = True
        self.target_activated: bool = True
        self.safety_margin: float = 5

        # General overlay configurations:
        self.offset_down: int = 5
        self.offset_right: int = 5
        self.transparency: float = 0.95
        self.font_size: int = 16
        self.text_padding: int = 4
        self.locked: bool = True

        if self.name in entries:
            add_entries_to_config(config_object=self, **entries[f"{self.name}"])


class RelativeConfig(OverlayConfig):
    """Class containing all configuration settings for relative overlay"""
    name = "relative"

    def __init__(self, **entries):
        # Relative specific configurations
        self.active: bool = True
        self.irating_activated: bool = True
        self.license_activated: bool = True
        self.hide_pits: bool = True
        self.nr_rows: int = 7
        self.nr_rows_front: int = 3
        self.driver_name_width: int = 16

        # General overlay configurations:
        self.offset_down: int = 850
        self.offset_right: int = 1350
        self.transparency: float = 0.95
        self.font_size: int = 16
        self.text_padding_x: int = 4
        self.text_padding_y: int = 4
        self.locked: bool = True

        if self.name in entries:
            add_entries_to_config(config_object=self, **entries[f"{self.name}"])


class SettingsConfig(Config):
    """Determines which settings menu are activated. Defaults to all inactive on start."""
    name = "settings"
    block_height = 100
    block_width = 200
    checkbutton_width = 10

    def __init__(self, **entries):
        self.fuel = False
        self.relative = False
        self.standings = False

        if self.name in entries:
            add_entries_to_config(config_object=self, **entries[f"{self.name}"])


class FontConfig(Config):
    """Class containing all configuration settings related to font appearance"""
    name = "font"

    def __init__(self, **entries):
        self.extra: str = "bold"
        self.size: int = 16
        self.style: str = "TkFixedFont"

        if self.name in entries:
            add_entries_to_config(config_object=self, **entries[f"{self.name}"])


class CompleteConfig(Config):
    """Configuration including all sub-components"""
    name = "complete"

    def __init__(self, **entries):
        self.auto_login: bool = False
        self.main_open: bool = True
        self.bg_color: str = '#1C1C1C'
        self.font = FontConfig(**entries)
        entries.pop(f"{FontConfig.name}", None)  # 'None' to avoid KeyError

        # Overlays
        self.fuel = FuelConfig(**entries)
        entries.pop(f"{FuelConfig.name}", None)
        self.relative = RelativeConfig(**entries)
        entries.pop(f"{RelativeConfig.name}", None)

        # Settings screens
        self.settings = SettingsConfig(**entries)
        entries.pop(f"{SettingsConfig.name}", None)

        add_entries_to_config(config_object=self, **entries)


def load_configuration() -> CompleteConfig:
    """Attempts to open and load the configuration file. Default if not found"""
    try:
        with open(r'config.yaml', encoding="utf-8") as config_file:
            entries = yaml.safe_load(config_file)
    except FileNotFoundError:
        logging.warning("config.yaml not found, loaded defaults instead")
        entries = {}

    # If the file that is available is empty, entries will be a NoneType
    if not entries:
        entries = {}  # must be converted to dict, before returning

    return CompleteConfig(**entries)


def object_to_dict(obj):
    """Converts the object to dict such that it can be correctly dumped to yaml. Credits to chatgpt, big CHAD"""
    if hasattr(obj, '__dict__'):
        return {k: object_to_dict(v) for k, v in obj.__dict__.items() if v is not None}
    if isinstance(obj, (list, tuple)):
        return [object_to_dict(x) for x in obj if x is not None]
    if isinstance(obj, dict):
        return {k: object_to_dict(v) for k, v in obj.items() if v is not None}

    return obj
