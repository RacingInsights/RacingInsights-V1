import tkinter

from src.backend.iRacing.state import State
from src.backend.iRacing.telemetry import Telemetry

from src.frontend.overlays.overlay_abstract import OverlayAbstract


class FuelColumn:
    def __init__(self, master, font, cfg, header_name, special_on):
        self.master = master
        self.font = font
        self.fg_header = cfg.fg_color_header
        self.fg_values = cfg.fg_color_values
        self.fg_special = cfg.fg_color_special
        self.bg = cfg.bg_color
        self.special_on = special_on
        self.text_padding = cfg.text_padding

        self.text_var = tkinter.StringVar()
        self.text_var.set("00.00")

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
            self.special_var.set("00.00")

            self.special = tkinter.Label(self.column_frame, textvariable=self.special_var, font=self.font,
                                         fg=self.fg_special,
                                         bg=self.bg, padx=self.text_padding, pady=self.text_padding)
            self.special.pack(pady=self.text_padding)

            self.all_labels.append(self.special)


class FuelScreen(OverlayAbstract):
    def __init__(self, parent_obj, telemetry: Telemetry, state: State, config_data, rounded=True):
        super().__init__(parent_obj, rounded, overlay_type="fuel", config_data=config_data)
        self.tm = telemetry
        self.state = state
        self.font = f'{self.cfg.font_style} {self.cfg.font_size} {self.cfg.font_extra}'

        self.create_fuelscreen_entries(respawn=False)

        if self.rounded:
            self.make_overlay_rounded()

    def update_values(self):
        """
        Loop that updates the frontend (dashboard) based on the data it gets from the backend (iRacing telemetry).
        Note that this function is supposed to be called in a different thread than the main
        :return:
        """
        # Update the frontend if still connected
        if self.state.ir_connected:
            self.update_widget_text_var("fuel_widget", self.tm.fuel)
            self.update_widget_text_var("last_widget", self.tm.cons)
            self.update_widget_text_var("avg_widget", self.tm.avg_cons)
            self.update_widget_text_var("target_widget", self.tm.target_cons_current)
            self.update_widget_special_var("target_widget", self.tm.target_cons_extra)
            self.update_widget_text_var("range_widget", self.tm.laps_left_current)
            self.update_widget_special_var("range_widget", self.tm.laps_left_extra)
            self.update_widget_text_var("refuel_widget", self.tm.refuel * (1 + self.cfg.safety_margin / 100))

    def update_widget_text_var(self, widget_name, tm_value):
        if hasattr(self, widget_name):
            widget_attr = getattr(self, widget_name)
            if hasattr(widget_attr, "text_var"):
                text_var = getattr(widget_attr, "text_var")
                text_var.set(f"{tm_value:.2f}")

    def update_widget_special_var(self, widget_name, tm_value):
        if hasattr(self, widget_name):
            widget_attr = getattr(self, widget_name)
            if hasattr(widget_attr, "special_var"):
                special_var = getattr(widget_attr, "special_var")
                special_var.set(f"{tm_value:.2f}")

    def update_visuals(self):
        """
        Used by the settingscheckbuttons to update the visual elements of the overlay
        :return:
        """
        self.font = f'{self.cfg.font_style} {self.cfg.font_size} {self.cfg.font_extra}'
        self.master.geometry(f"+{self.cfg.offset_right}+{self.cfg.offset_down}")

        self.create_fuelscreen_entries(respawn=True)

        self.overlay_frame.update()  # Important, otherwise it will not have the updated tk widgets

        for widget in self.activated_widgets:
            if widget:  # To ensure it's not None
                for label in widget.all_labels:
                    if hasattr(label, "configure"):
                        label.configure(font=self.font)
                        label.update()

        if self.rounded:
            self.make_overlay_rounded()

    def create_fuelscreen_entries(self, respawn):
        if respawn:
            # Instead of checking whether a widget was already active and then updating it,
            # it's easier to just delete the entire frame and starting over
            self.overlay_frame.pack_forget()
            self.overlay_frame.destroy()

            self.overlay_frame = tkinter.Frame(master=self.overlay_canvas, bg=self.cfg.bg_color)
            self.overlay_frame.pack()

            if self.rounded:
                # Create a temporary window, just to spawn the widgets before calculating/spawning the final window
                self.overlay_canvas.create_window(0, 0, window=self.overlay_frame)

        list_of_widgets = ["fuel", "last", "avg", "target", "range", "refuel"]
        self.activated_widgets = []

        # Create the widgets in case they are activated in cfg, put in self.activated_widgets
        for widget_name in list_of_widgets:
            if not getattr(self.cfg, f"{widget_name}_activated"): # If widget shouldn't be activated, set to None
                setattr(self, f"{widget_name}_widget", None)
                self.activated_widgets.append(getattr(self, f"{widget_name}_widget"))
            else:  # If widget should be activated, spawn a FuelColumn instance with customized header name
                special_on = False  # Default
                if widget_name == 'target' or widget_name == 'range':
                    special_on = True

                setattr(self, f"{widget_name}_widget",
                        FuelColumn(master=self.overlay_frame, font=self.font, cfg=self.cfg,
                                   header_name=f"{widget_name}".title(),
                                   special_on=special_on))
                self.activated_widgets.append(getattr(self, f"{widget_name}_widget"))
