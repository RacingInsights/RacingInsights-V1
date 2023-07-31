from configparser import ConfigParser

# Get the configparser object
config_object = ConfigParser()

# Create the entries
config_object["FUELOVERLAY"] = {
    "text_padding": 15,
    "offset_right": 5,
    "offset_down": 5,
    "bg_color": "#000054",
    "fg_color_header": "#EEEEEE",
    "fg_color_values": "#24fc03",
    "fg_color_special": "#ff0000"
}

config_object["COLORS"] = {
    "bg_color": "#222222",
    "fg_color": "#EEEEEE",
    "button_color": "RED"
}

config_object["FONT"] = {
    "font_style": "TkFixedFont",
    "font_size": 16,
    "font_extra": "bold",
}

config_object["MAINMENUDIMENSIONS"] = {
    "button_width": 15,
    "button_height": 1
}

# Write the above sections to config.ini file
with open('../previous_versions/Version_Before_Refactor/src/frontend/config.ini', 'w') as conf:
    config_object.write(conf)
