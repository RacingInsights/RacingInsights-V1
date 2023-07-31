import tkinter
from enum import Enum
from typing import List, Optional

from src.backend.iRacing.overlay_telemetries.relative_telemetry import LappedState, RelativeEntry, RelativeTelemetry
from src.frontend.overlay import Overlay
from src.frontend.utils.RoundedBorder import RoundedBorder
from src.frontend.utils.RoundedLabelFrame import RoundedLabelFrame
from src.frontend.utils.ri_event_handler import RIEventTypes, subscribe
from src.startup.my_configuration import CompleteConfig


class FontColors(Enum):
    GOLD = "#FAC213"
    BLUE_DARK = "#001949"
    BLUE = "#003AA5"
    GREY_DARK = "#515151"
    RED_DARK = "#680000"
    RED = "#D30000"
    WHITE = "#FFFFFF"


class RelativeRow:
    """Class for the row instances that make up the relative"""

    def update(self):
        # Configuration of the visual based on telemetry
        self.update_visual_configuration()

        # Show the new values representing the telemetry
        self.update_string_vars()

    def __init__(self, master: tkinter.Frame, configuration: CompleteConfig):
        # Elements: Position | Car nr | Driver name | *License | *irating | relative time
        self.master = master
        self.configuration = configuration
        self.telemetry: Optional[RelativeEntry] = None
        subscribe(event_type=RIEventTypes.RELATIVE_FEATURE_CHANGE, fn=self.update_event_handler)

        self.frame = tkinter.Frame(master=self.master, bg=self.configuration.bg)

        self.previous_value_color = FontColors.WHITE.value

        self.position = tkinter.StringVar()
        self.car_nr = tkinter.StringVar()
        self.driver_name = tkinter.StringVar()
        self.license = tkinter.StringVar()
        self.irating = tkinter.StringVar()
        self.relative_time = tkinter.StringVar()

        self.pos_frame = tkinter.Frame(master=self.frame, bg=self.configuration.bg)

        self.position_label = tkinter.Label(master=self.frame,
                                            textvariable=self.position,
                                            font=self.font,
                                            fg=self.value_color,
                                            bg=self.configuration.bg,
                                            padx=self.x_padding,
                                            anchor='w',
                                            width=2,
                                            )

        self.car_nr_label = tkinter.Label(master=self.frame,
                                          textvariable=self.car_nr,
                                          font=self.font,
                                          fg=self.value_color,
                                          bg=self.configuration.bg,
                                          padx=self.x_padding,
                                          anchor='w',
                                          width=2
                                          )

        self.driver_name_label = tkinter.Label(master=self.frame,
                                               textvariable=self.driver_name,
                                               font=self.font,
                                               fg=self.value_color,
                                               bg=self.configuration.bg,
                                               padx=self.x_padding,
                                               anchor='w'
                                               )

        self.license_label = RoundedLabelFrame(master=self.frame,
                                               textvariable=self.license,
                                               font_size=self.font_size,
                                               font_color="BLACK",
                                               bg=self.configuration.bg,
                                               fill=self.license_color,
                                               padx=self.x_padding,
                                               )

        self.irating_label = RoundedLabelFrame(master=self.frame,
                                               textvariable=self.irating,
                                               font_size=self.font_size,
                                               font_color="BLACK",
                                               bg=self.configuration.bg,
                                               fill=self.irating_color,
                                               padx=self.x_padding,
                                               )

        self.relative_time_label = tkinter.Label(master=self.frame,
                                                 textvariable=self.relative_time,
                                                 font=self.font,
                                                 fg=self.value_color,
                                                 bg=self.configuration.bg,
                                                 padx=self.x_padding,
                                                 anchor='e',
                                                 width=4
                                                 )

        self.pack_activated()
        self.update_event_handler()

    def set_telemetry(self, relative_entry: Optional[RelativeEntry]):
        """Called from outside by the RelativeOverlay"""
        self.telemetry = relative_entry

    @property
    def license_color(self) -> str:
        if not self.telemetry:
            return self.configuration.bg
        match self.telemetry.license[0]:
            case "P":
                return "BLACK"
            case "A":
                return "BLUE"
            case "B":
                return "GREEN"
            case "C":
                return "YELLOW"
            case "D":
                return "ORANGE"
            case "R":
                return "RED"

    @property
    def irating_color(self) -> str:
        if not self.telemetry:
            return self.configuration.bg
        ir = self.telemetry.irating
        if ir < 500:
            return "#430000"
        if ir < 1000:
            return "#820000"
        if ir < 1500:
            return "#BC0700"
        if ir < 2000:
            return "#FF3900"
        if ir < 2500:
            return "#FFBA00"
        if ir < 3000:
            return "#FFE100"
        if ir < 4000:
            return "#B8FF00"
        if ir < 5000:
            return "#18FF07"
        if ir < 6000:
            return "#00F7CF"
        if ir < 7000:
            return "#00ADFF"
        if ir < 8000:
            return "#005AF7"
        if ir < 9000:
            return "#0018EF"
        if ir < 10000:
            return "#3A07AC"
        else:
            return "#420063"

    @property
    def value_color(self) -> str:
        if not self.telemetry:
            return FontColors.WHITE.value
        if self.telemetry.is_player:
            return FontColors.GOLD.value
        if self.telemetry.in_pits:
            if self.telemetry.lapped_state == LappedState.BACKMARKER:
                return FontColors.BLUE_DARK.value
            if self.telemetry.lapped_state == LappedState.LAPPING:
                return FontColors.RED_DARK.value
            else:
                return FontColors.GREY_DARK.value
        if self.telemetry.lapped_state == LappedState.BACKMARKER:
            return FontColors.BLUE.value
        if self.telemetry.lapped_state == LappedState.LAPPING:
            return FontColors.RED.value
        return FontColors.WHITE.value

    @property
    def font_size(self) -> int:
        return self.configuration.relative.font_size

    @property
    def font(self):
        return f"{self.configuration.font.style} " \
               f"{self.font_size} " \
               f"{self.configuration.font.extra}"

    @property
    def x_padding(self):
        return self.configuration.relative.text_padding_x

    @property
    def y_padding(self):
        return self.configuration.relative.text_padding_y

    def disable(self):
        """Disables the specific column"""
        for label in self.frame.winfo_children():
            label.pack_forget()
        self.frame.pack_forget()

    def pack_activated(self):
        """Enables the specific column"""
        self.frame.pack(expand=1)
        self.pos_frame.pack(side='left', expand=1, fill='both')
        self.position_label.pack(fill='both', side='left')
        self.car_nr_label.pack(fill='both', side='left')
        self.driver_name_label.pack(side="left", expand=1, fill='both')
        if self.configuration.relative.license_activated:
            self.license_label.pack(side='left')
        if self.configuration.relative.irating_activated:
            self.irating_label.pack(side='left')
        self.relative_time_label.pack(fill='both')

    def update_visual_configuration(self):
        new_color = self.value_color
        if self.telemetry:
            # No need to update all widgets if color is still same as previous
            if not new_color == self.previous_value_color:
                # To optimize, avoiding the winfo_children call, configure manually instead:
                self.position_label.configure(fg=new_color)
                self.car_nr_label.configure(fg=new_color)
                self.driver_name_label.configure(fg=new_color)
                self.relative_time_label.configure(fg=new_color)

            # Experimental
            self.irating_label.fill = self.irating_color
            self.irating_label.change_rounded_rectangle_color()
            self.license_label.fill = self.license_color
            self.license_label.change_rounded_rectangle_color()

        else:
            self.irating_label.fill = self.configuration.bg_color
            self.irating_label.change_rounded_rectangle_color()
            self.license_label.fill = self.configuration.bg_color
            self.license_label.change_rounded_rectangle_color()

        self.previous_value_color = new_color

    def update_string_vars(self):
        if self.telemetry:
            self.position.set(value=str(self.telemetry.position))
            self.car_nr.set(value=str(self.telemetry.car_nr))
            self.driver_name.set(value=self.telemetry.driver_name)
            self.license.set(value=self.telemetry.license)
            self.irating.set(value=str(self.telemetry.irating))
            self.relative_time.set(value="{:.1f}".format(self.telemetry.relative_time))

        else:
            self.position.set(value="")
            self.car_nr.set(value="")
            self.driver_name.set(value="")
            self.license.set(value="")
            self.irating.set(value="")
            self.relative_time.set(value="")

    def update_event_handler(self):
        """Subscribed to the change event"""
        self.frame.configure(pady=self.y_padding)

        self.position_label.configure(font=self.font, padx=self.x_padding)
        self.car_nr_label.configure(font=self.font, padx=self.x_padding)
        self.driver_name_label.configure(font=self.font, padx=self.x_padding)
        self.relative_time_label.configure(font=self.font, padx=self.x_padding)

        self.irating_label.padx = self.x_padding
        self.irating_label.font_size = self.font_size
        self.irating_label.configure()

        self.license_label.padx = self.x_padding
        self.license_label.font_size = self.font_size
        self.license_label.configure()

        self.driver_name_label.configure(width=self.configuration.relative.driver_name_width)


class RelativeOverlay(Overlay):
    """Relative screen overlay"""
    MAX_DRIVERS = 9

    def set_offset_right(self, offset_right):
        self.configuration.relative.offset_right = offset_right

    def set_offset_down(self, offset_down):
        self.configuration.relative.offset_down = offset_down

    @property
    def active(self) -> bool:
        """
        This flag is used as reference to whether the overlay should be active (updated) or not
        :return:
        """
        return self.configuration.relative.active

    @property
    def locked(self) -> bool:
        """
        This flag is used as reference to whether the overlay should be locked (for dragging) or not
        :return:
        """
        return self.configuration.relative.locked

    @property
    def offset_right(self) -> int:
        return self.configuration.relative.offset_right

    @property
    def offset_down(self) -> int:
        return self.configuration.relative.offset_down

    def _on_closing(self):
        """
        Determines the behavior when the overlay is closed
        :return:
        """
        self.configuration.relative.active = False  # Otherwise it will crash because it still thinks it's active

    def __init__(self, root: tkinter.Tk, configuration: CompleteConfig, telemetry: RelativeTelemetry):
        super().__init__(root=root)
        self.configuration = configuration
        self.telemetry = telemetry

        self.overlay.title("Relative")
        self.overlay.geometry(f"+{self.offset_right}+{self.offset_down}")
        self.overlay.attributes('-alpha', self.configuration.relative.transparency)
        self.set_correct_visibility()

        self.relative_rows: List[Optional[RelativeRow]] = []

        subscribe(event_type=RIEventTypes.RELATIVE_FEATURE_CHANGE, fn=self.reset_activations)
        subscribe(event_type=RIEventTypes.RELATIVE_FEATURE_CHANGE, fn=self.update_transparency)

        # Create a frame to hold the table - with rounded border!
        self.table_frame = RoundedBorder(master=self.overlay, bg=self.configuration.bg)

        self.initialized_rows = [RelativeRow(master=self.table_frame.frame, configuration=self.configuration) for _ in
                                 range(self.MAX_DRIVERS)]

    def populate_relative_rows(self):
        for row in self.relative_rows:
            row.disable()

        self.relative_rows = []

        for i in range(self.nr_of_rows):
            self.relative_rows.append(self.initialized_rows[i])

        for row in self.relative_rows:
            row.pack_activated()
            row.update_event_handler()

    def update_transparency(self):
        self.overlay.attributes('-alpha', self.configuration.relative.transparency)

    @property
    def hide_pits(self) -> bool:
        return self.configuration.relative.hide_pits

    @property
    def player_index(self) -> int:
        """Refers to the id of the player in the sorted and filtered relative_time entry telemetry list"""
        return self.filter_pits_data(_data=self.telemetry.sorted_relative_entries,
                                     middle_index=self.telemetry.player_id_in_sorted)[1]

    @property
    def relative_entries(self) -> List[Optional[RelativeEntry]]:
        return self.filter_pits_data(_data=self.telemetry.sorted_relative_entries,
                                     middle_index=self.telemetry.player_id_in_sorted)[0]

    @property
    def nr_of_rows(self) -> int:
        return self.configuration.relative.nr_rows

    @property
    def nr_of_rows_front(self) -> int:
        """Determines how many drivers are shown in front of the player in relative_time"""
        return min(self.configuration.relative.nr_rows_front, self.nr_of_rows)

    @property
    def offset(self) -> int:
        """
        Offset that indicates where to start looking in the relative_telemetry.sorted_relative_entries
        to include the correct number of relative rows and keep the player in the desired location of
        the relative overlay.
        It just serves the purpose of being a parameter for further calculations.
        """
        return int(max(self.player_index - self.nr_of_rows_front, - self.nr_of_rows_front))

    def filter_pits_data(self, _data: List[Optional[RelativeEntry]], middle_index: int):
        data = []
        index = middle_index

        if self.hide_pits:
            for i, car in enumerate(_data):
                if car.in_pits and not car.is_player:
                    if i < middle_index:
                        index -= 1  # Change the index pointing to the player in case cars in pits should be ignored
                else:
                    data.append(car)

        if not self.hide_pits:
            data = _data
        return data, index

    def update_rows(self):
        for i, row in enumerate(self.relative_rows):
            # Set the telemetry for row
            if i + self.offset < 0 or i + self.offset > len(self.relative_entries) - 1:
                row.set_telemetry(relative_entry=None)
            else:
                row.set_telemetry(relative_entry=self.relative_entries[i + self.offset])

            # Update row based on set telemetry
            row.update()

    def reset_activations(self):
        """
        This is necessary to change the appearance when either the license/irating feature is enabled or disabled.
        This method needs to be subscribed to event of RELATIVE_FEATURE_CHANGE
        """
        for row in self.relative_rows:
            row.disable()

        for row in self.relative_rows:
            row.pack_activated()

    def ensure_correct_row_initialization(self):
        # Ensure correct nr of rows is set
        if len(self.relative_rows) != self.nr_of_rows:
            self.populate_relative_rows()

    def update(self) -> None:
        self.set_correct_visibility()
        if not self.active:
            return

        self.ensure_correct_row_initialization()

        # Update each row
        self.update_rows()
