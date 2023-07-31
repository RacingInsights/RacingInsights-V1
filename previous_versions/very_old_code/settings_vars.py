from configparser import ConfigParser

# ------------------------------------ Appearance settings -----------------------------------------------------
config_object = ConfigParser()
config_object.read("config.ini")
# -- Dimensions
# FONT_SIZE = 16
FONT_SIZE = int(config_object["FONT"]["font_size"])
assert 0 <= FONT_SIZE <= 100

# # TEXT_PADDING = 15
TEXT_PADDING = int(config_object["FUELOVERLAYDIMENSIONS"]["text_padding"])
assert 0 <= TEXT_PADDING <= 100


BUTTON_WIDTH = 15
BUTTON_HEIGHT = 1

# # Automatically calculate the block dimensions with text padding as a customizable setting
# block_width, block_height = int(FONT_SIZE * 4.5 + TEXT_PADDING), int(FONT_SIZE * 5 + TEXT_PADDING)
#
# target_sub_height = int(block_height / 3)

# -- Colors
color_dark_bg = "#222222"
color_navy_bg = "#000054"
color_neon_green = "#24fc03"
color_red_fg = "#ff0000"
color_white = "#EEEEEE"

fg_color = color_white
fg_color_vals = color_neon_green
fg_color_extra_vals = color_red_fg

OFFSET_RIGHT = int(5)
OFFSET_DOWN = int(5)

FONT_STYLE = "TkFixedFont"
FONT_EXTRA = "bold"

# FONT = f'{FONT_STYLE} {FONT_SIZE} {FONT_EXTRA}'
