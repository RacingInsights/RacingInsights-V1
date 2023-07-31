import tkinter
from tkinter import ttk, Tk

from PIL import ImageTk, Image

from previous_versions.Version_Before_Refactor.src.backend.iRacing.state import State
from previous_versions.Version_Before_Refactor.src.backend.iRacing.telemetry import Telemetry
from previous_versions.Version_Before_Refactor.src.frontend.configurations import MainScreenConfig
from previous_versions.Version_Before_Refactor.src.frontend.overlays.fuelscreen import FuelScreen
from previous_versions.Version_Before_Refactor.src.frontend.overlays.relativescreen import RelativeScreen
from previous_versions.Version_Before_Refactor.src.frontend.settingscreens.fuelsettings import FuelSettingsScreen
from previous_versions.Version_Before_Refactor.src.frontend.settingscreens.relativesettings import RelativeSettingsScreen


class MainScreen:
    def __init__(self, master: Tk, telemetry: Telemetry, state: State, config_data, ui_reference):
        self.settings_app = None
        self.relative_app = None
        self.fuel_app = None
        self.ui_reference = ui_reference
        self.linked_queue = self.ui_reference.ui_queue
        self.cfg = MainScreenConfig(**config_data['main'])
        self.cfg_data = config_data

        self.master = master
        self.master.deiconify()  # Because master Tk is withdrawn when auto-log in occurs
        self.master.title("RacingInsights")
        self.master.config(width=self.cfg.width, height=self.cfg.height, bg=self.cfg.bg_color)

        self.open_in_middle()
        self.master.iconbitmap("images/RacingInsights_Logo.ico")

        self.telemetry = telemetry
        self.state = state

        logo_img = Image.open("images/RacingInsights_Icon.png")
        logo_img = logo_img.resize((286, 286))
        logo_photo_img = ImageTk.PhotoImage(logo_img)

        logo_label = tkinter.Label(master=self.master, image=logo_photo_img, bg=self.cfg.bg_color)
        logo_label.image = logo_photo_img
        logo_label.pack(pady=50)

        settings_img = Image.open("images/Settings.png")
        settings_img = settings_img.resize((24, 24))
        settings_photo_img = ImageTk.PhotoImage(settings_img)

        # The image needs to be added to a label for it to show in a button... (No need to pack though)
        settings_label = tkinter.Label(master=self.master, image=settings_photo_img, bg=self.cfg.bg_color)
        settings_label.image = settings_photo_img

        fuel_row = tkinter.Frame(self.master, bg=self.cfg.bg_color, width=200, height=30)
        fuel_row.pack(pady=10)

        self.fuel_button = ttk.Button(fuel_row, text='Fuel overlay', width=self.cfg.button_width,
                                      command=self.open_close_fuel)
        self.fuel_button.pack(pady=5, padx=5, side='left')
        self.fuelsettings_button = ttk.Button(fuel_row, image=settings_photo_img, command=self.open_fuel_settings)
        self.fuelsettings_button.pack(pady=0, padx=5, side='left')

        relative_row = tkinter.Frame(self.master, bg=self.cfg.bg_color, width=200, height=30)
        relative_row.pack(pady=10)

        self.relative_button = ttk.Button(relative_row, text='Relative overlay', width=self.cfg.button_width,
                                          command=self.open_close_relative)
        self.relative_button.pack(pady=5, padx=5, side='left')
        self.relativesettings_button = ttk.Button(relative_row, image=settings_photo_img,
                                                  command=self.open_relative_settings)
        self.relativesettings_button.pack(pady=0, padx=5, side='left')

        self.relative_open = False
        self.fuel_open = False
        self.settings_open = False

        self.relative_toggle_in_progress = False
        self.fuel_toggle_in_progress = False

        if self.cfg.relative_open_on_startup:
            self.open_close_relative()

        if self.cfg.fuel_open_on_startup:
            self.open_close_fuel()

    def open_in_middle(self):
        # get screen width and height
        screen_width = self.master.winfo_screenwidth()  # width of the screen
        screen_height = self.master.winfo_screenheight()  # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (screen_width / 2) - (self.cfg.width / 2)
        y = (screen_height / 2) - (self.cfg.height / 2)

        # set the dimensions of the screen and where it is placed
        self.master.geometry(f"{self.cfg.width}x{self.cfg.height}+{int(x)}+{int(y)}")

    def open_close_fuel(self):
        """
        Method to open or close the fuelscreen. This method is called on a buttonpress (async event),
        hence it puts the jobs in a queue to avoid disrupting the update method that is looking for certain widgets.
        :return:
        """
        # Prevent the button to activate multiple jobs when pressed repeatedly in quick succession (before the jobs finish)
        if self.fuel_toggle_in_progress:
            return

        self.fuel_toggle_in_progress = True

        if not self.fuel_open:
            self.linked_queue.put((self.open_fuel, None))

        elif self.fuel_open:
            self.linked_queue.put((self.close_fuel, None))

    def open_fuel(self):
        self.fuel_app = FuelScreen(parent_obj=self, telemetry=self.telemetry, state=self.state,
                                   config_data=self.cfg_data, rounded=True)
        self.fuel_open = True
        self.fuel_toggle_in_progress = False

    def close_fuel(self):
        # Do not close the overlay when the settings are open
        if not self.settings_open:
            self.fuel_app.master.destroy()
            self.fuel_open = False

        # The toggling job is now finished
        self.fuel_toggle_in_progress = False

    def open_fuel_settings(self):
        """
        Opens the fuel settings window. This settings window can be used to change the appearance of the overlay.
        :return:
        """
        if not self.settings_open:
            if not self.fuel_open:
                self.linked_queue.put((self.open_fuel, None))

            self.linked_queue.put((self.open_fuel_settings_job, None))

    def open_fuel_settings_job(self):
        self.settings_app = FuelSettingsScreen(parent_obj=self, config_data=self.cfg_data, linked_app=self.fuel_app,
                                               cfg_key="fuel")

        self.settings_open = True

    def open_close_relative(self):
        """
        Method to open or close the relative. This method is called on a buttonpress (async event),
        hence it puts the jobs in a queue to avoid disrupting the update method that is looking for certain widgets.
        :return:
        """
        # Prevent the button to activate multiple jobs when pressed repeatedly in quick succession (before the jobs finish)
        if self.relative_toggle_in_progress:
            return

        self.relative_toggle_in_progress = True

        if not self.relative_open:
            self.linked_queue.put((self.open_relative, None))

        elif self.relative_open:
            self.linked_queue.put((self.close_relative, None))

    def open_relative(self):
        self.relative_app = RelativeScreen(parent_obj=self, telemetry=self.telemetry, state=self.state,
                                           config_data=self.cfg_data, rounded=True)
        self.relative_open = True
        self.relative_toggle_in_progress = False

    def close_relative(self):
        # Do not close the overlay when the settings are open
        if not self.settings_open:
            self.relative_app.master.destroy()
            self.relative_open = False

        # The toggling job is now finished
        self.relative_toggle_in_progress = False

    def open_relative_settings(self):
        """
        Opens the relative settings window. This settings window can be used to change the appearance of the overlay.
        :return:
        """
        if not self.settings_open:
            if not self.relative_open:
                self.linked_queue.put((self.open_relative, None))

            self.linked_queue.put((self.open_relative_settings_job, None))

    def open_relative_settings_job(self):
        """
        This method is added to the queue in order to avoid creation when self.relative_app is not available yet.
        In this queue, it will always be called after self.relative_app has been created.
        :return:
        """
        self.settings_app = RelativeSettingsScreen(parent_obj=self, config_data=self.cfg_data,
                                                   linked_app=self.relative_app, cfg_key="relative")
        self.settings_open = True

    def update(self):
        if self.fuel_app and self.fuel_open:
            self.fuel_app.update_telemetry_values()
        if self.relative_app and self.relative_open:
            self.relative_app.update_telemetry_values()
