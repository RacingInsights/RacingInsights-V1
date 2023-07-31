from dataclasses import dataclass
from pprint import pprint

import yaml


@dataclass
class FuelScreenConfig:
    font_size: int = 15
    bg_color: str = "#222222"

    # def __post_init__(self):
    #     for key, value in self.__dict__.items():
    #         if not isinstance(value, type(FuelScreenConfig.__dict__[key])):
    #             print(f"Yaml-file value for {key} is of type {type(value)}")
    #             self.__dict__[key] = FuelScreenConfig.__dict__[key]


# yaml_data = """font_size: "19"
# bg_color: "#222222"
# """

# data = yaml.safe_load(yaml_data)

data = {'bg_color': '#222222', 'font_size': '19'}
pprint(data)
print(type(data))
fuelscreen_config = FuelScreenConfig(**data)

print(fuelscreen_config)