from configparser import ConfigParser
import logging


# global FONT_SIZE, TEXT_PADDING, BUTTON_WIDTH, BUTTON_HEIGHT, OFFSET_RIGHT, \
#     OFFSET_DOWN, FONT_STYLE, FONT_EXTRA, BG_COLOR


def load_config(screen_obj):
    """
    Loads the config and assigns its content to global variables
    :return:
    """
    # Load the config object
    config_object = ConfigParser()
    available_config = config_object.read("src/frontend/config.ini")

    # Make a new default config if no config is available
    if not available_config:
        logging.info("No config is available. Creating a new default config.ini")
        config_object = create_default_config()

    # Load the properties specific for the FuelScreen
    screen_obj_type = f"{type(screen_obj)}"
    if screen_obj_type.find('FuelScreen') != -1:
        logging.info("Loaded the config properties specific to FuelScreen")
        screen_obj.font_size = int(float(config_object["FUELSCREEN"]["font_size"]))
        screen_obj.offset_right = int(float(config_object["FUELSCREEN"]["offset_right"]))
        screen_obj.offset_down = int(float(config_object["FUELSCREEN"]["offset_down"]))
        screen_obj.text_padding = int(float(config_object["FUELSCREEN"]["text_padding"]))

        screen_obj.bg_color = config_object["FUELSCREEN"]["bg_color"]
        screen_obj.bg_color_special = config_object["FUELSCREEN"]["bg_color_special"]
        screen_obj.color_header = config_object["FUELSCREEN"]["fg_color_header"]
        screen_obj.color_values = config_object["FUELSCREEN"]["fg_color_values"]
        screen_obj.color_special = config_object["FUELSCREEN"]["fg_color_special"]

        screen_obj.font_style = config_object["GENERAL"]["font_style"]
        screen_obj.font_extra = config_object["GENERAL"]["font_extra"]
        screen_obj.fuel_activated = bool(int(config_object["FUELSCREEN"]["fuel_activated"]))
        screen_obj.last_activated = bool(int(config_object["FUELSCREEN"]["last_activated"]))
        screen_obj.avg_activated = bool(int(config_object["FUELSCREEN"]["avg_activated"]))
        screen_obj.target_activated = bool(int(config_object["FUELSCREEN"]["target_activated"]))
        screen_obj.range_activated = bool(int(config_object["FUELSCREEN"]["range_activated"]))
        screen_obj.refuel_activated = bool(int(config_object["FUELSCREEN"]["refuel_activated"]))

    else:
        screen_obj.button_width = int(float(config_object["GENERAL"]["button_width"]))
        screen_obj.button_height = int(float(config_object["GENERAL"]["button_height"]))
        screen_obj.button_color = config_object["GENERAL"]["button_color"]

        screen_obj.font_size = int(float(config_object["GENERAL"]["font_size"]))
        screen_obj.font_style = config_object["GENERAL"]["font_style"]
        screen_obj.font_extra = config_object["GENERAL"]["font_extra"]

        screen_obj.bg_color = config_object["GENERAL"]["bg_color"]
        screen_obj.fg_color = config_object["GENERAL"]["fg_color"]


def create_default_config():
    """
    Creates a new config.ini file without default values
    :return:
    """
    # Get the configparser object
    config_object = ConfigParser()

    # Create the entries
    config_object["FUELSCREEN"] = {
        "font_size": 16,
        "bg_color": "#222222",
        "bg_color_special": "#000054",
        "text_padding": 15,
        "offset_right": 5,
        "offset_down": 5,
        "fg_color_header": "#0061B7",
        "fg_color_values": "#EAEAEA",
        "fg_color_special": "#E12D5C",
        "fuel_activated": 1,
        "last_activated": 1,
        "avg_activated": 1,
        "target_activated": 1,
        "range_activated": 1,
        "refuel_activated": 1,
    }

    config_object["GENERAL"] = {
        "font_size": 16,
        "bg_color": "#222222",  # Not used
        "fg_color": "#EEEEEE",  # Not used
        "button_color": "RED",  # Not used
        "button_width": 20,
        "button_height": 1,
        "font_style": "TkFixedFont",
        "font_extra": "bold"
    }

    # Write the above sections to config.ini file
    with open('src/frontend/config.ini', 'w') as conf:
        config_object.write(conf)

    return config_object


def save_in_config(**kwargs):
    # Load the config object
    config_object = ConfigParser()
    available_config = config_object.read("src/frontend/config.ini")

    # Make a new default config if no config is available
    if not available_config:
        logging.info("No config is available. Creating a new default config.ini")
        config_object = create_default_config()

    # Can be optimized more
    for key, value in kwargs.items():
        for section in config_object.sections():
            if section == value[0]:
                for cfg_key in config_object[f"{section}"].keys():
                    if cfg_key == key:
                        config_object.set(section=section, option=key, value=f"{value[1]}")
                        logging.info(f"Updated {key}:{value[1]} in [{section}] and saved it in config.ini")

    # Write the updated config_object to config.ini file
    with open('src/frontend/config.ini', 'w') as conf:
        config_object.write(conf)
