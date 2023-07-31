import copy
import tkinter

from previous_versions.Version_Before_Refactor.src.backend.iRacing.state import State
from previous_versions.Version_Before_Refactor.src.backend.iRacing.telemetry import Telemetry
from previous_versions.Version_Before_Refactor.src.backend.utils.exception_handler import exception_handler
from previous_versions.Version_Before_Refactor.src.frontend.overlays.overlay_abstract import OverlayAbstract
from previous_versions.Version_Before_Refactor.src.frontend.overlays.utils.rounded_box import RoundedBox


class RelativeEntry:
    def __init__(self, master, cfg, color="WHITE"):
        self.cfg = cfg
        self.padding_x = self.cfg.text_padding_x
        self.padding_y = self.cfg.text_padding_y
        self.font = f'TkFixedFont {self.cfg.font_size} bold'
        self.font_box = f'TkFixedFont {self.get_font_box_size(self.cfg.font_size)} bold'
        self.color = color

        self.pos = tkinter.StringVar()
        self.car_class = tkinter.StringVar()
        self.car_nr = tkinter.StringVar()
        self.brand = tkinter.StringVar()
        self.driver_name = tkinter.StringVar()
        self.driver_license = tkinter.StringVar()
        self.irating = tkinter.StringVar()
        self.relative_time = tkinter.StringVar()

        self.master = master

        self.bg_color = "#1C1C1C"

        self.entry_frame = tkinter.Frame(master=self.master, bg=self.bg_color)
        self.entry_frame.pack(expand=1)

        self.create_relative_entry_elements(respawn=False)

        self.set_bg_color()

    def update_appearance_attributes(self, cfg):
        self.cfg = cfg
        self.padding_x = self.cfg.text_padding_x
        self.padding_y = self.cfg.text_padding_y
        self.font = f'TkFixedFont {self.cfg.font_size} bold'
        self.font_box = f'TkFixedFont {self.get_font_box_size(self.cfg.font_size)} bold'

    def update_telemetry_values(self, entry_data=None, session_type=None, laps_ir=None):
        """
        :param entry_data:
        :param session_type:
        :param laps_ir:
        :return:
        """
        if entry_data is not None:
            self.set_entry_color(entry_data, session_type, laps_ir)
            self.set_class_color(class_color=entry_data['car_class_color'])
            self.set_license_color(license_color=entry_data['license_color'])
            self.set_irating_color(irating=entry_data['irating'])
            self.set_string_vars(entry_data)
        elif entry_data is None:
            self.set_class_color(class_color=int(self.bg_color[1:], 16))
            self.set_license_color(license_color=int(self.bg_color[1:], 16))
            self.set_irating_color()
            self.set_string_vars()

    def update_appearance(self, cfg):
        """
        Configure() and update() all tk/custom elements in the relative_entry
        :return:
        """
        self.update_appearance_attributes(cfg)

        for label in self.all_labels:
            label.configure(font=self.font, padx=self.padding_x, pady=self.padding_y)
            label.update()

        for box in self.all_boxes:
            box.configure(font=self.font_box, padding_x=self.padding_x, padding_y=self.padding_y)
            box.update()

    def set_class_color(self, class_color: int):
        if class_color == 0:  # If the car class color was set to 0 by iracing, then don't show background color
            class_color = int(self.bg_color[1:], 16)

        color = f'#{hex(class_color)[2:]}'.upper()  # remove 0x and add #
        while len(color) < 7:
            color = self.insert(color, '0',
                                1)  # Make sure the length is according to what tkinter expects (length 7 including #)

        self.car_nr_box.bg_in = color
        self.car_nr_box.configure(bg=color)
        self.car_nr_box.update()

    def set_license_color(self, license_color: int):
        if not self.cfg.license_activated:
            return

        color = f'#{hex(license_color)[2:]}'.upper()  # remove 0x and add #
        while len(color) < 7:
            color = self.insert(color, '0',
                                1)  # Make sure the length is according to what tkinter expects (length 7 including #)
        self.driver_license_box.bg_in = color
        self.driver_license_box.configure(bg=color)
        self.driver_license_box.update()

    @staticmethod
    def insert(source_str, insert_str, pos):
        return source_str[:pos] + insert_str + source_str[pos:]

    @staticmethod
    def get_irating_color(irating):
        if not irating:
            color = "#1C1C1C"
            return color

        color = "#000000"
        if 499 < irating < 1000:
            color = "#B50000"
        elif irating < 1250:
            color = "#B53300"
        elif irating < 1500:
            color = "#B27400"
        elif irating < 1750:
            color = "#98AF00"
        elif irating < 2000:
            color = "#4EAD00"
        elif irating < 2500:
            color = "#00AA08"
        elif irating < 3000:
            color = "#00A580"
        elif irating < 4000:
            color = "#0077A3"
        elif irating < 5000:
            color = "#0025A0"
        elif irating < 6000:
            color = "#882AA8"
        elif irating >= 6000:
            color = "#9E008E"
        return color

    @staticmethod
    def get_font_box_size(font_size):
        return int(font_size - 0.1 * font_size)

    def set_irating_color(self, irating: int = None):
        if not self.cfg.irating_activated:
            return

        color = self.get_irating_color(irating)
        self.irating_box.bg_in = color
        self.irating_box.configure(bg=color)
        self.irating_box.update()

    def set_string_vars(self, entry_data=None):
        if entry_data is not None:
            self.pos.set(f"{entry_data['class_position']}")
            self.car_nr.set(f"#{entry_data['car_nr']}")
            self.brand.set(f"{entry_data['car_brand']}")
            self.driver_name.set(f"{entry_data['driver_name']}")
            self.driver_license.set(f"{entry_data['ir_license']}")
            self.irating.set(f"{entry_data['irating']}")
            self.relative_time.set("{:.1f}".format(entry_data['relative']))

        elif entry_data is None:
            self.pos.set("")
            self.car_nr.set("")
            self.brand.set("")
            self.driver_name.set("")
            self.driver_license.set("")
            self.irating.set("")
            self.relative_time.set("")

    def set_entry_color(self, entry_data, session_type, laps_ir):
        gold = "#FAC213"
        blue_dark = "#001949"
        blue = "#003AA5"
        grey_dark = "#515151"
        red_dark = "#680000"
        red = "#D30000"
        white = "#FFFFFF"

        if entry_data['is_player']:  # Always use gold color for player
            self.set_fg_color(gold)
        elif session_type == 'Practice':  # If it's a practice session, don't use colors for back-markers or ahead
            if entry_data['in_pit']:
                self.set_fg_color(grey_dark)
            else:
                self.set_fg_color(white)

        elif entry_data['in_pit']:  # If the car is in the pits, use darker colors
            if entry_data['laps'] <= laps_ir:  # Back-marker
                self.set_fg_color(blue_dark)
            elif entry_data['laps'] > laps_ir + 1:  # Lap(s) ahead of player
                self.set_fg_color(red_dark)
            else:
                self.set_fg_color(grey_dark)

        else:  # Not the player and not in pits, use the normal colors
            if entry_data['laps'] <= laps_ir:  # Back-marker
                self.set_fg_color(blue)
            elif entry_data['laps'] > laps_ir + 1:  # Lap(s) ahead of player
                self.set_fg_color(red)
            else:
                self.set_fg_color(white)

    def set_fg_color(self, color: str):
        self.color = color
        for label in self.all_labels:
            label.configure(fg=self.color)
            label.update()

    def set_bg_color(self):
        for label in self.all_labels:
            label.configure(bg=self.bg_color)

    def create_relative_entry_elements(self, respawn):
        """
        Populates the relative entry with the desired elements based on the current cfg values
        :return:
        """
        if respawn:
            # To respawn a relative entry, forget, destroy and repack
            self.entry_frame.pack_forget()
            self.entry_frame.destroy()
            self.entry_frame = tkinter.Frame(master=self.master, bg=self.bg_color)
            self.entry_frame.pack(expand=1)

        self.all_boxes = []

        self.pos_frame = tkinter.Frame(master=self.entry_frame, bg=self.bg_color)
        self.driver_name_frame = tkinter.Frame(master=self.entry_frame, bg=self.bg_color)
        self.relative_time_frame = tkinter.Frame(master=self.entry_frame, bg=self.bg_color)

        self.pos_label = tkinter.Label(master=self.pos_frame, textvariable=self.pos, width=2, font=self.font,
                                       fg=self.color, anchor='w', padx=self.padding_x, pady=self.padding_y)
        self.driver_name_label = tkinter.Label(master=self.driver_name_frame, textvariable=self.driver_name, width=16,
                                               font=self.font, fg=self.color, anchor='w', padx=self.padding_x,
                                               pady=self.padding_y)
        self.relative_time_label = tkinter.Label(master=self.relative_time_frame, textvariable=self.relative_time,
                                                 width=4, font=self.font, fg=self.color, anchor='e',
                                                 padx=self.padding_x, pady=self.padding_y)

        self.pos_frame.pack(side='left', expand=1, fill='both')
        self.car_nr_box = RoundedBox(master=self.entry_frame, bg_out=self.bg_color, bg_in=self.bg_color,
                                     textvariable=self.car_nr, font=self.font_box, padding_x=self.padding_x,
                                     padding_y=self.padding_y, box_width=4)
        self.all_boxes.append(self.car_nr_box)
        self.driver_name_frame.pack(side='left', expand=1, fill='both')

        if self.cfg.license_activated:
            self.driver_license_box = RoundedBox(master=self.entry_frame, bg_out=self.bg_color, bg_in=self.bg_color,
                                                 textvariable=self.driver_license, font=self.font_box,
                                                 padding_x=self.padding_x, padding_y=self.padding_y, box_width=5)
            self.all_boxes.append(self.driver_license_box)

        if self.cfg.irating_activated:
            self.irating_box = RoundedBox(master=self.entry_frame, bg_out=self.bg_color, bg_in=self.bg_color,
                                          textvariable=self.irating, font=self.font_box, padding_x=self.padding_x,
                                          padding_y=self.padding_y,
                                          box_width=4)
            self.all_boxes.append(self.irating_box)

        self.relative_time_frame.pack(side='left', expand=1, fill='both')
        self.pos_label.pack(fill='both')
        self.driver_name_label.pack(fill='both', expand=1)
        self.relative_time_label.pack(fill='both')

        self.all_labels = [self.pos_label, self.driver_name_label, self.relative_time_label]


class RelativeScreen(OverlayAbstract):
    def __init__(self, parent_obj, telemetry: Telemetry, state: State, config_data, rounded=True):
        super().__init__(parent_obj, rounded, overlay_type="relative", config_data=config_data)
        self.state: State = state
        self.telemetry: Telemetry = telemetry
        self.relative_entries: list[RelativeEntry] = []

        self.create_relative_entries(respawn=False)

        if self.rounded:
            self.make_overlay_rounded()

        self.master.deiconify()
        self.master.title("RacingInsights - Relative")

    @exception_handler
    def update_telemetry_values(self):
        """
        The new values in self.telemetry are set in the corresponding stringvars
        :return:
        """
        if not self.state.ir_connected or self.telemetry.relative_data is None:
            if self.parent_obj.settings_open:
                self.update_widgets_with_dummy_values()
            return

        # Make a deepcopy to avoid data being updated from the outside (= from the backend) during this loop
        copied_data = copy.deepcopy(self.telemetry.relative_data)
        middle_index = copy.deepcopy(self.telemetry.player_location_in_sorted)

        # If user wants to hide cars in pits, remove these from the telemetry data
        data, index = self.filter_pits_data(copied_data, middle_index)

        self.update_telemetry_values_relative_entries(data, index)

    def update_telemetry_values_relative_entries(self, data, index):
        """
        Update relative entries based on telemetry data
        :param data:
        :param index:
        :return:
        """
        offset = int(max(index - 3, -3))

        for i in range(7):  # For all 7 entries
            widget = self.relative_entries[i]
            # for these ranges, no data is available hence pass None to the widget
            if i + offset < 0 or i + offset > len(data) - 1:
                widget.update_telemetry_values()
            else:  # call update_entry to populate the specific entry widget with data
                widget.update_telemetry_values(entry_data=data[i + offset],
                                               session_type=self.telemetry.session_type,
                                               laps_ir=self.telemetry.laps_ir)

    def filter_pits_data(self, copied_data, middle_index):
        data = []
        index = middle_index
        if self.cfg.hide_pits:
            for i, car in enumerate(copied_data):
                if car["in_pit"] and not car["is_player"]:
                    if i < middle_index:
                        index -= 1  # Change the index pointing to the player in case cars in pits should be ignored
                else:
                    data.append(car)

        if not self.cfg.hide_pits:
            data = copied_data

        return data, index

    def update_appearance(self):
        """
        For each relative_entry call the relative_entry.update_appearance method
        This configures and updates the already existing tk or custom elements.
        Note, this doesn't destroy any widgets, it only updates!
        After all individual elements are updated, it updates the container frame
        and recalculates the rounded border.
        :return:
        """
        self.master.wm_withdraw() # Make the changes while the TopLevel is invisible

        for relative_entry in self.relative_entries:
            relative_entry.update_appearance(self.cfg)

        if self.rounded:
            self.make_overlay_rounded()

        self.master.wm_deiconify()

    def reconstruct_overlay(self):
        """
        Destroys the current overlay_frame instance and rebuilds it for the currently activated elements
        :return:
        """
        self.master.geometry(f"+{self.cfg.offset_right}+{self.cfg.offset_down}")
        self.create_relative_entries(respawn=True)
        if self.rounded:
            self.make_overlay_rounded()

    def update_widgets_with_dummy_values(self):
        relative_dummies = [3, 2.5, 1.2, 0, -1, -3.3, -10]
        irating_dummies = [6001, 5320, 4200, 3333, 2750, 2250, 1900]
        pits_dummies = [True, False, False, False, False, False, False]

        for i in range(7):  # For all 7 entries

            dummy_data = {"relative": relative_dummies[i],
                          "car_nr": i,
                          "driver_name": f"Name{i} Surname{i}",
                          "car_brand": "car brand",
                          "irating": irating_dummies[i],
                          "ir_license": "A 4.99",
                          "license_color": 87003,
                          "car_id": i,
                          "class_position": i,
                          "car_class_name": "car class",
                          "car_class_color": 6969420,
                          "in_pit": pits_dummies[i],
                          "laps": 12,
                          "is_player": False}

            if i == 3:
                dummy_data['is_player'] = True

            if self.cfg.hide_pits:  # Just showing what it would look like, not same implementation as actual function
                if i == 0:
                    dummy_data = None
            self.relative_entries[i].update_telemetry_values(entry_data=dummy_data, session_type='Practice', laps_ir=7)

    def create_relative_entries(self, respawn):
        """
        Sets and populates the list of relative_entries with RelativeEntry elements
        :return:
        """
        if respawn:
            self.overlay_frame.pack_forget()
            self.overlay_frame.destroy()

            self.overlay_frame = tkinter.Frame(master=self.overlay_canvas, bg=self.cfg.bg_color)
            self.overlay_frame.pack()

            self.relative_entries.clear()  # Keeps the attribute but clears its content (perhaps desired over del here)

            if self.rounded:
                # Create a temporary window, just to spawn the widgets before calculating/spawning the final window
                self.overlay_canvas.create_window(0, 0, window=self.overlay_frame)

        for i in range(7):  # Relative overlay has 7 entries (3 above the player, the player, 3 below the player)
            color = None
            if i == 3:  # The 4th relative entry widget (index=3) is the player, give this a gold color
                color = "#FAC213"

            self.relative_entries.append(
                RelativeEntry(master=self.overlay_frame, cfg=self.cfg, color=color))
