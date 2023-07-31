import tkinter

from previous_versions.Version_Before_Refactor.src.backend.iRacing.state import State
from previous_versions.Version_Before_Refactor.src.backend.iRacing.telemetry import Telemetry
from previous_versions.Version_Before_Refactor.src.backend.utils.exception_handler import exception_handler
from previous_versions.Version_Before_Refactor.src.frontend.overlays.overlay_abstract import OverlayAbstract


class FuelColumn:
    def __init__(self, master, cfg, header_name, special_on):
        self.master = master
        self.cfg = cfg
        self.font = f'{self.cfg.font_style} {self.cfg.font_size} {self.cfg.font_extra}'

        self.fg_header = cfg.fg_color_header
        self.fg_values = cfg.fg_color_values
        self.fg_special = cfg.fg_color_special
        self.bg = cfg.bg_color
        self.special_on = special_on
        self.text_padding = cfg.text_padding

        self.text_var = tkinter.StringVar()
        self.text_var.set("     ")

        self.column_frame = tkinter.Frame(master=self.master, bg=self.bg)
        self.column_frame.pack(side='left', anchor='nw', expand=1, fill='both')

        self.header = tkinter.Label(self.column_frame, text=header_name, font=self.font, fg=self.fg_header, bg=self.bg,
                                    padx=self.text_padding, pady=self.text_padding)
        self.header.pack(expand=0, side='top')

        self.value = tkinter.Label(self.column_frame, textvariable=self.text_var, font=self.font, fg=self.fg_values,
                                   bg=self.bg, padx=self.text_padding, pady=self.text_padding)
        self.value.pack(expand=1, anchor='center', fill='both')

        self.all_labels = [self.header, self.value]

        if self.special_on:
            self.special_var = tkinter.StringVar()
            self.special_var.set("     ")

            self.special = tkinter.Label(self.column_frame, textvariable=self.special_var, font=self.font,
                                         fg=self.fg_special,
                                         bg=self.bg, padx=self.text_padding, pady=self.text_padding)
            self.special.pack(pady=self.text_padding)

            self.all_labels.append(self.special)

    def update_appearance_attributes(self, cfg):
        self.cfg = cfg
        self.text_padding = self.cfg.text_padding
        self.font = f'{self.cfg.font_style} {self.cfg.font_size} {self.cfg.font_extra}'

    def update_appearance(self, cfg):
        """
        Configure() and update() all tk/custom elements in the fuel_column
        :return:
        """
        self.update_appearance_attributes(cfg)

        for label in self.all_labels:
            label.configure(font=self.font, padx=self.text_padding, pady=self.text_padding)
            label.update()


class FuelScreen(OverlayAbstract):
    def __init__(self, parent_obj, telemetry: Telemetry, state: State, config_data, rounded=True):
        super().__init__(parent_obj, rounded, overlay_type="fuel", config_data=config_data)
        self.font: str | None = None
        self.state: State = state
        self.telemetry: Telemetry = telemetry
        self.fuel_columns: list[FuelColumn] = []

        self.create_fuelscreen_entries(respawn=False)

        if self.rounded:
            self.make_overlay_rounded()

        self.master.wm_deiconify()
        self.master.title("RacingInsights - Fuel calculator")

    @exception_handler
    def update_telemetry_values(self):
        """
        The new values in self.telemetry are set in the corresponding stringvars
        :return:
        """
        if not self.state.ir_connected:
            if self.parent_obj.settings_open:
                self.update_widgets_with_dummy_values()

        elif self.state.ir_connected:
            self.update_widget_text_var("fuel_widget", self.telemetry.fuel)
            self.update_widget_text_var("last_widget", self.telemetry.cons)
            self.update_widget_text_var("avg_widget", self.telemetry.avg_cons)
            self.update_widget_text_var("target_widget", self.telemetry.target_cons_current)
            self.update_widget_special_var("target_widget", self.telemetry.target_cons_extra)
            self.update_widget_text_var("range_widget", int(self.telemetry.laps_left_current))
            self.update_widget_special_var("range_widget", int(self.telemetry.laps_left_extra))
            self.update_widget_text_var("refuel_widget", self.telemetry.refuel * (1 + self.cfg.safety_margin / 100))
            self.update_widget_text_var("finish_widget", self.telemetry.target_finish)
            self.update_widget_text_var("remaining_widget", int(self.telemetry.laps_left_in_race))

    def update_widgets_with_dummy_values(self):
        self.update_widget_text_var("fuel_widget", float(0))
        self.update_widget_text_var("last_widget", float(0))
        self.update_widget_text_var("avg_widget", float(0))
        self.update_widget_text_var("target_widget", float(0))
        self.update_widget_special_var("target_widget", float(0))
        self.update_widget_text_var("range_widget", int(0))
        self.update_widget_special_var("range_widget", int(0))
        self.update_widget_text_var("refuel_widget", float(0))
        self.update_widget_text_var("finish_widget", float(0))
        self.update_widget_text_var("remaining_widget", int(0))

    def update_widget_special_var(self, widget_name, tm_value):
        if tm_value < 0:  # Not valid, set to 0 instead
            tm_value = 0

        if hasattr(self, widget_name):
            widget_attr = getattr(self, widget_name)
            if hasattr(widget_attr, "special_var"):
                special_var = getattr(widget_attr, "special_var")
                if isinstance(tm_value, int):
                    special_var.set(f"{tm_value}")
                else:
                    special_var.set(f"{tm_value:.2f}")

    def update_widget_text_var(self, widget_name, tm_value):
        if tm_value < 0:  # Not valid, set to 0 instead
            tm_value = 0

        if hasattr(self, widget_name):
            widget_attr = getattr(self, widget_name)
            if hasattr(widget_attr, "text_var"):
                text_var = getattr(widget_attr, "text_var")
                if isinstance(tm_value, int):
                    text_var.set(f"{tm_value}")
                else:
                    text_var.set(f"{tm_value:.2f}")

    def update_appearance(self):
        self.master.wm_withdraw()
        for fuel_column in self.fuel_columns:
            if fuel_column:  # Make sure it's not None
                fuel_column.update_appearance(self.cfg)

        self.overlay_frame.update()

        if self.rounded:
            self.make_overlay_rounded()
        self.master.wm_deiconify()

    def reconstruct_overlay(self):
        """
        Destroys the current overlay_frame instance and rebuilds it for the currently activated elements
        :return:
        """
        self.font = f'{self.cfg.font_style} {self.cfg.font_size} {self.cfg.font_extra}'
        self.master.geometry(f"+{self.cfg.offset_right}+{self.cfg.offset_down}")

        self.create_fuelscreen_entries(respawn=True)

        self.overlay_frame.update()  # Important, otherwise it will not have the updated tk widgets

        for widget in self.fuel_columns:
            if widget:  # To ensure it's not None
                for label in widget.all_labels:
                    if hasattr(label, "configure"):
                        label.configure(font=self.font)
                        label.update()

        if self.rounded:
            self.make_overlay_rounded()

    def create_fuelscreen_entries(self, respawn):
        """
        Sets and populates the list of fuel_columns with FuelColumn elements
        :return:
        """
        if respawn:
            self.overlay_frame.pack_forget()
            self.overlay_frame.destroy()

            self.overlay_frame = tkinter.Frame(master=self.overlay_canvas, bg=self.cfg.bg_color)
            self.overlay_frame.pack()

            self.fuel_columns.clear()

            if self.rounded:
                # Create a temporary window, just to spawn the widgets before calculating/spawning the final window
                self.overlay_canvas.create_window(0, 0, window=self.overlay_frame)

        list_of_widgets = ["fuel", "last", "avg", "target", "range", "refuel", "finish", "remaining"]

        # Create the widgets in case they are activated in cfg, put in self.fuel_columns
        for widget_name in list_of_widgets:
            underscored_widget_name = widget_name.replace(" ", "_").replace("\n", "_")
            if not getattr(self.cfg,
                           f"{underscored_widget_name}_activated"):  # If widget shouldn't be activated, set to None
                setattr(self, f"{underscored_widget_name}_widget", None)
                self.fuel_columns.append(getattr(self, f"{underscored_widget_name}_widget"))
            else:  # If widget should be activated, spawn a FuelColumn instance with customized header name
                special_on = False  # Default
                if widget_name == 'target' or widget_name == 'range':
                    special_on = True

                setattr(self, f"{underscored_widget_name}_widget",
                        FuelColumn(master=self.overlay_frame, cfg=self.cfg,
                                   header_name=f"{widget_name}".title(),
                                   special_on=special_on))
                self.fuel_columns.append(getattr(self, f"{underscored_widget_name}_widget"))
