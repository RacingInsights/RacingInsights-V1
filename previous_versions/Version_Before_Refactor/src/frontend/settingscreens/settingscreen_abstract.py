import logging
import tkinter
from tkinter import ttk, messagebox

import yaml

from previous_versions.Version_Before_Refactor.src.frontend.configurations import SettingsScreenConfig, FuelScreenConfig, RelativeScreenConfig


class SettingsCheckButton:
    def __init__(self, master, cfg, parent_obj, linked_app, name: str, setting_name: str):
        self.master = master
        self.cfg = cfg
        self.parent_obj = parent_obj
        self.setting_name = setting_name
        self.linked_app = linked_app
        self.linked_queue = self.parent_obj.ui_reference.ui_queue

        self.checkbutton_frame = ttk.Frame(self.master, width=self.cfg.block_width, height=self.cfg.block_height)
        self.checkbutton_frame.pack(pady=5, anchor='nw')

        self.bool_var = tkinter.BooleanVar()
        self.bool_var.set(getattr(self.linked_app.cfg, self.setting_name))
        self.checkbutton = ttk.Checkbutton(master=self.checkbutton_frame, text=name,
                                           variable=self.bool_var,
                                           command=self.toggle_activation,
                                           onvalue=True, offvalue=False)

        self.checkbutton.pack(pady=5, fill='both', anchor='nw')

    def toggle_activation(self):
        arguments = (self.linked_app.cfg, self.setting_name, self.bool_var.get())
        self.linked_queue.put((setattr, arguments))

        if not self.linked_app.__class__.__name__ == 'MainScreen':
            self.linked_queue.put((self.linked_app.reconstruct_overlay, None))


class SettingScreenAbstract:
    def __init__(self, parent_obj, config_data, linked_app, cfg_key: str):
        self.y = None
        self.x = None
        self.parent_obj = parent_obj
        self.master = tkinter.Toplevel(self.parent_obj.master)
        self.cfg = SettingsScreenConfig(**config_data['settings'])
        self.cfg_data = config_data

        self.linked_queue = self.parent_obj.ui_reference.ui_queue

        self.app = linked_app
        self.unlock_app()
        self.cfg_key = cfg_key  # "fuel", "relative", etc

        self.master.config(bg=self.cfg.bg_color)
        self.master.iconbitmap("images/RacingInsights_Settings.ico")
        self.master.title("Settings")

        self.open_in_middle()

        self.master.lift()

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def set_window_size(self):
        """
        Changes the geometry of the master window in case desired dimensions are given
        (if not given, the window's size will automatically adjust to contents inside)
        """
        if self.cfg.width and self.cfg.height:
            self.master.geometry('%dx%d' % (self.cfg.width, self.cfg.height))

    def open_in_middle(self):
        """
        Opens the window in the middle of the screen
        :return:
        """
        self.set_window_size()

        # get screen width and height
        screen_width = self.master.winfo_screenwidth()  # width of the screen
        screen_height = self.master.winfo_screenheight()  # height of the screen

        # calculate x and y coordinates for the Toplevel master window
        x = (screen_width / 2) - (self.cfg.width / 2)
        y = (screen_height / 2) - (self.cfg.height / 2)

        # Add offsets to center the window
        self.master.geometry(f"+{int(x)}+{int(y)}")

    def on_closing(self):
        if messagebox.askyesno(title="Unsaved settings", message="Would you like to save these current settings?"):
            logging.info("The user asked to save the settings in the config file")
            self.save_settings_in_config()
        else:
            logging.info("The user asked not to save the settings, current config is reloaded")

            match self.cfg_key:
                case "fuel":
                    self.app.cfg = FuelScreenConfig(**self.cfg_data["fuel"])
                case "relative":
                    self.app.cfg = RelativeScreenConfig(**self.cfg_data["relative"])

            self.linked_queue.put((self.app.reconstruct_overlay, None))

        self.parent_obj.settings_open = False  # Currently no distinction is made between the different setting menus
        self.lock_app()
        logging.info("Settings window closed")
        self.master.destroy()

    def save_settings_in_config(self):
        main_changed_cfg = self.parent_obj.cfg.__dict__  # needed to save {overlay_name}_open_on_startup setting in main
        overlay_changed_cfg = self.app.cfg.__dict__  # needed to save overlay specific settings
        config_dict = self.cfg_data
        config_dict["main"] = main_changed_cfg
        config_dict[f"{self.cfg_key}"] = overlay_changed_cfg
        with open(r'config_data.yaml', 'w') as file:
            _ = yaml.dump(config_dict, file)

    def unlock_app(self):
        self.app.set_drag_bind(True)
        self.app.locked = False

    def lock_app(self):
        if not self.app.locked:
            self.app.set_drag_bind(False)
            self.app.locked = True

    def toggle_app_lock(self):
        self.app.locked = not self.app.locked

        if not self.app.locked:
            self.app.set_drag_bind(True)
        else:
            self.app.set_drag_bind(False)
