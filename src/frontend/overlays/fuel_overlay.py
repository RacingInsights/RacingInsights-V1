import tkinter

from src.backend.iRacing.overlay_telemetries.fuel_telemetry import FuelTelemetry
from src.frontend.overlay import Overlay
from src.frontend.utils.RoundedBorder import RoundedBorder
from src.frontend.utils.ri_event_handler import RIEventTypes, subscribe
from src.startup.my_configuration import CompleteConfig


class FuelColumn:
    header_color = "#0061B7"
    value_color = "#EAEAEA"

    def __init__(self, master: tkinter.Frame, configuration: CompleteConfig, header_name: str,
                 telemetry_ref):
        self.master = master
        self.configuration = configuration
        self.telemetry_reference = telemetry_ref
        self.state = False

        self.frame = tkinter.Frame(master=self.master, bg=self.configuration.bg)

        self.header = tkinter.Label(master=self.frame,
                                    text=header_name,
                                    font=self.font,
                                    fg=self.header_color,
                                    bg=self.configuration.bg,
                                    padx=self.x_padding,
                                    pady=self.y_padding
                                    )

        self.value_variable = tkinter.StringVar()

        self.value = tkinter.Label(master=self.frame,
                                   textvariable=self.value_variable,
                                   font=self.font,
                                   fg=self.value_color,
                                   bg=self.configuration.bg,
                                   padx=self.x_padding,
                                   pady=self.y_padding
                                   )

    @property
    def font(self):
        return f"{self.configuration.font.style} " \
               f"{self.configuration.fuel.font_size} " \
               f"{self.configuration.font.extra}"

    @property
    def x_padding(self):
        return self.configuration.fuel.text_padding

    @property
    def y_padding(self):
        return self.configuration.fuel.text_padding

    def update(self, desired_state: bool):
        # Activation
        self.set_correct_activation_state(desired_state)

        # Telemetry values update
        self.value_variable.set("{:.2f}".format(self.telemetry_reference.value))

    def set_correct_activation_state(self, desired_state: bool):
        """Sets the activation state to match what is desired (based on configuration)"""
        if self.state is False and desired_state is True:
            self.enable()
        if self.state is True and desired_state is False:
            self.disable()
        self.state = desired_state

    def update_visual_configuration(self):
        """Assumes that any updates from outside to the configuration are visible here. Configures accordingly.
        Called by overlay when overlay receives event"""
        for widget in self.frame.winfo_children():
            if isinstance(widget, tkinter.Label):
                widget.configure(font=self.font,
                                 padx=self.x_padding,
                                 pady=self.y_padding)

    def disable(self):
        """Disables the specific column"""
        self.frame.pack_forget()
        self.header.pack_forget()
        self.value.pack_forget()

    def enable(self):
        """Enables the specific column"""
        self.frame.pack(side='left', anchor='nw', expand=1, fill='both')
        self.header.pack(expand=0, side='top')
        self.value.pack(expand=1, anchor='center', fill='both')

    def update_configuration(self, configuration) -> None:
        """Observer method to update configuration when new available"""
        self.configuration = configuration


class FuelOverlay(Overlay):
    """Fuel screen overlay"""

    def set_offset_right(self, offset_right):
        self.configuration.fuel.offset_right = offset_right

    def set_offset_down(self, offset_down):
        self.configuration.fuel.offset_down = offset_down

    @property
    def active(self) -> bool:
        """
        This flag is used as reference to whether the overlay should be active (updated) or not
        :return:
        """
        return self.configuration.fuel.active

    @property
    def locked(self) -> bool:
        """
        This flag is used as reference to whether the overlay should be locked (for dragging) or not
        :return:
        """
        return self.configuration.fuel.locked

    @property
    def offset_right(self) -> int:
        return self.configuration.fuel.offset_right

    @property
    def offset_down(self) -> int:
        return self.configuration.fuel.offset_down

    def _on_closing(self):
        """
        Determines the behavior when the overlay is closed
        :return:
        """
        self.configuration.fuel.active = False  # Otherwise it will crash because it still thinks it's active

    def __init__(self, root: tkinter.Tk, configuration: CompleteConfig, telemetry: FuelTelemetry):
        super().__init__(root=root)
        self.configuration = configuration
        self.telemetry = telemetry
        subscribe(event_type=RIEventTypes.FUEL_FEATURE_CHANGE, fn=self.update_feature_event_handler)

        self.overlay.title("Fuel calculator")
        self.overlay.geometry(f"+{self.offset_right}+{self.offset_down}")
        self.overlay.attributes('-alpha', self.configuration.fuel.transparency)
        self.set_correct_visibility()

        self.table_frame = RoundedBorder(master=self.overlay, bg=self.configuration.bg)

        # All fuel columns
        self.fuel_live_col = FuelColumn(master=self.table_frame.frame,
                                        configuration=self.configuration,
                                        header_name="Fuel",
                                        telemetry_ref=self.telemetry.fuel
                                        )

        self.last_consumption_col = FuelColumn(master=self.table_frame.frame,
                                               configuration=self.configuration,
                                               header_name="Last",
                                               telemetry_ref=self.telemetry.last_consumption
                                               )

        self.avg_cons_col = FuelColumn(master=self.table_frame.frame,
                                       configuration=self.configuration,
                                       header_name="Avg",
                                       telemetry_ref=self.telemetry.average_consumption
                                       )

        self.target_cons_col = FuelColumn(master=self.table_frame.frame,
                                          configuration=self.configuration,
                                          header_name="Target",
                                          telemetry_ref=self.telemetry.target_consumption_extra
                                          )

        self.range_col = FuelColumn(master=self.table_frame.frame,
                                    configuration=self.configuration,
                                    header_name="Range",
                                    telemetry_ref=self.telemetry.range_laps
                                    )

        self.refuel_col = FuelColumn(master=self.table_frame.frame,
                                     configuration=self.configuration,
                                     header_name="Refuel",
                                     telemetry_ref=self.telemetry.refuel_amount
                                     )

        self.target_cons_finish_col = FuelColumn(master=self.table_frame.frame,
                                                 configuration=self.configuration,
                                                 header_name="Finish",
                                                 telemetry_ref=self.telemetry.target_consumption_finish
                                                 )

    def update_feature_event_handler(self):
        """Called when an event is posted. Needs to be subscribed!"""
        all_fuel_columns = [
            (self.fuel_live_col, self.configuration.fuel.fuel_activated),
            (self.last_consumption_col, self.configuration.fuel.last_activated),
            (self.avg_cons_col, self.configuration.fuel.avg_activated),
            (self.target_cons_col, self.configuration.fuel.target_activated),
            (self.range_col, self.configuration.fuel.range_activated),
            (self.refuel_col, self.configuration.fuel.refuel_activated),
            (self.target_cons_finish_col, self.configuration.fuel.finish_activated),
        ]
        for col in all_fuel_columns:
            if col[1]:
                col[0].update_visual_configuration()

    def update(self) -> None:
        """Method that updates the overlay each time a new telemetry sample is taken"""
        self.set_correct_visibility()
        if not self.active:
            return

        all_fuel_columns = [
            (self.fuel_live_col, self.configuration.fuel.fuel_activated),
            (self.last_consumption_col, self.configuration.fuel.last_activated),
            (self.avg_cons_col, self.configuration.fuel.avg_activated),
            (self.target_cons_col, self.configuration.fuel.target_activated),
            (self.range_col, self.configuration.fuel.range_activated),
            (self.refuel_col, self.configuration.fuel.refuel_activated),
            (self.target_cons_finish_col, self.configuration.fuel.finish_activated),
        ]

        self.overlay.attributes('-alpha', self.configuration.fuel.transparency)

        activations = [item[1] for item in all_fuel_columns]
        if not any(activations):
            self.configuration.fuel.active = False

        for item in all_fuel_columns:
            item[0].update(desired_state=item[1])
