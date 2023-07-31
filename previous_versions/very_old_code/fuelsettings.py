import logging
import tkinter
from functools import partial
from tkinter import messagebox, ttk

import yaml

from src.frontend.configurations import FuelScreenConfig
from src.frontend.settingscreens.settingscreen_abstract import SettingScreenAbstract

from src.frontend.hover_info import HoverInfoWindow


class FuelSettingsScreen(SettingScreenAbstract):
    def __init__(self, parent_obj, config_data):
        super().__init__(parent_obj, config_data)
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Make sure to open the fuel app before opening the UI elements in SettingsScreen linked to the fuel app
        self.parent_obj.open_close_fuel()

        # Initialize the widgets
        self.fontsize_frame = ttk.Frame(self.master, width=self.cfg.block_width, height=self.cfg.block_height)
        self.fontsize_frame.pack(pady=10)

        self.fontsize_label = ttk.Label(self.fontsize_frame, text="Font size", anchor='center')
        self.fontsize_label.pack(fill='both', pady=10)
        self.fontsize_slider = ttk.Scale(self.fontsize_frame, from_=9, to=30, orient='horizontal',
                                         command=self.set_font_size, length=self.cfg.block_width)

        self.fontsize_slider.set(self.parent_obj.fuel_app.cfg.font_size)
        self.fontsize_slider.pack(padx=5)

        self.textpadding_frame = ttk.Frame(self.master, width=self.cfg.block_width, height=self.cfg.block_height)
        self.textpadding_frame.pack(pady=10)

        self.textpadding_label = ttk.Label(self.textpadding_frame, text="Text padding", anchor='center')
        self.textpadding_label.pack(fill='both', pady=10)
        self.textpadding_slider = ttk.Scale(self.textpadding_frame, from_=0, to=40, orient='horizontal',
                                            command=self.set_text_padding, length=self.cfg.block_width)

        self.textpadding_slider.set(self.parent_obj.fuel_app.cfg.text_padding)
        self.textpadding_slider.pack(padx=5)

        self.lockbutton = ttk.Button(self.master, text='Toggle Fuel Lock', width=self.cfg.button_width,
                                     command=self.toggle_fuel_lock)
        self.lockbutton.pack(pady=10)

        # Add a hover info window to explain the button's functionality
        self.lockbutton_hover_info = HoverInfoWindow(master_widget=self.lockbutton,
                                                     text="lock or unlock the fuel overlay to position it to your liking")

        self.checkbutton_frame = ttk.Frame(self.master, width=self.cfg.block_width, height=self.cfg.block_height)
        self.checkbutton_frame.pack(pady=10)

        self.fuel_activated_var = tkinter.BooleanVar()
        self.fuel_activated_var.set(self.parent_obj.fuel_app.cfg.fuel_activated)
        self.fuel_checkbutton = ttk.Checkbutton(master=self.checkbutton_frame, text='Fuel',
                                                variable=self.fuel_activated_var,
                                                command=partial(self.toggle_activation,
                                                                fuel_activated=self.fuel_activated_var),
                                                onvalue=True, offvalue=False)
        self.fuel_checkbutton.pack(pady=5, fill='both')

        self.last_activated_var = tkinter.BooleanVar()
        self.last_activated_var.set(self.parent_obj.fuel_app.cfg.last_activated)
        self.last_checkbutton = ttk.Checkbutton(master=self.checkbutton_frame, text='Last',
                                                variable=self.last_activated_var,
                                                command=partial(self.toggle_activation,
                                                                last_activated=self.last_activated_var),
                                                onvalue=True, offvalue=False)
        self.last_checkbutton.pack(pady=5, fill='both')

        self.avg_activated_var = tkinter.BooleanVar()
        self.avg_activated_var.set(self.parent_obj.fuel_app.cfg.avg_activated)
        self.avg_checkbutton = ttk.Checkbutton(master=self.checkbutton_frame, text='Average',
                                               variable=self.avg_activated_var,
                                               command=partial(self.toggle_activation,
                                                               avg_activated=self.avg_activated_var),
                                               onvalue=True, offvalue=False)
        self.avg_checkbutton.pack(pady=5, fill='both')

        self.target_activated_var = tkinter.BooleanVar()
        self.target_activated_var.set(self.parent_obj.fuel_app.cfg.target_activated)
        self.target_checkbutton = ttk.Checkbutton(master=self.checkbutton_frame, text='Target',
                                                  variable=self.target_activated_var,
                                                  command=partial(self.toggle_activation,
                                                                  target_activated=self.target_activated_var),
                                                  onvalue=True, offvalue=False)
        self.target_checkbutton.pack(pady=5, fill='both')

        self.range_activated_var = tkinter.BooleanVar()
        self.range_activated_var.set(self.parent_obj.fuel_app.cfg.range_activated)
        self.range_checkbutton = ttk.Checkbutton(master=self.checkbutton_frame, text='Range',
                                                 variable=self.range_activated_var,
                                                 command=partial(self.toggle_activation,
                                                                 range_activated=self.range_activated_var),
                                                 onvalue=True, offvalue=False)
        self.range_checkbutton.pack(pady=5, fill='both')

        self.refuel_activated_var = tkinter.BooleanVar()
        self.refuel_activated_var.set(self.parent_obj.fuel_app.cfg.refuel_activated)
        self.refuel_checkbutton = ttk.Checkbutton(master=self.checkbutton_frame, text='Refuel',
                                                  variable=self.refuel_activated_var,
                                                  command=partial(self.toggle_activation,
                                                                  refuel_activated=self.refuel_activated_var),
                                                  onvalue=True, offvalue=False)
        self.refuel_checkbutton.pack(pady=5, fill='both')

    def on_closing(self):
        if messagebox.askyesno(title="Unsaved settings", message="Would you like to save these current settings?"):
            logging.info("The user asked to save the settings in the config file")
            self.save_settings_in_config()
        else:
            logging.info("The user asked not to save the settings, current config is reloaded")
            self.parent_obj.fuel_app.cfg = FuelScreenConfig(**self.cfg_data["fuel"])
            self.parent_obj.fuel_app.update_visuals()
        self.parent_obj.cfg.settings_open = False
        self.lock_fuel_lock()
        logging.info("Settings window closed")
        self.master.destroy()

    def save_settings_in_config(self):
        fuel_dict = self.parent_obj.fuel_app.cfg.__dict__
        config_dict = self.cfg_data
        config_dict["fuel"] = fuel_dict
        with open(r'config_data.yaml', 'w') as file:
            documents = yaml.dump(config_dict, file)

    def lock_fuel_lock(self):
        if not self.parent_obj.fuel_app.locked:
            self.parent_obj.fuel_app.set_drag_bind(False)
            self.parent_obj.fuel_app.locked = True

    def toggle_fuel_lock(self):
        self.parent_obj.fuel_app.locked = not self.parent_obj.fuel_app.locked

        if not self.parent_obj.fuel_app.locked:
            self.parent_obj.fuel_app.set_drag_bind(True)
        else:
            self.parent_obj.fuel_app.set_drag_bind(False)

    def set_font_size(self, value):
        font_size = int(float(value))
        self.parent_obj.fuel_app.resize_text(font_size=font_size)

    def set_text_padding(self, value):
        text_padding = int(float(value))
        self.parent_obj.fuel_app.resize_padding(text_padding=text_padding)

    def toggle_activation(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self.parent_obj.fuel_app.cfg, key,
                    value.get())  # set the attribute that matches the name of the key to the specified value
            self.parent_obj.fuel_app.update_visuals()
