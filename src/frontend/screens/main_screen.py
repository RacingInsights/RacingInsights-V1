import tkinter
from tkinter import ttk

from PIL import Image, ImageTk

from src.frontend.screen import IconTypes, Screen
from src.frontend.utils.ri_event_handler import RIEventTypes, post_event
from src.startup.my_configuration import CompleteConfig


class MainScreen(Screen):
    """Main screen used to change configuration settings, these settings are read by overlays"""

    @property
    def icon(self) -> IconTypes:
        return IconTypes.LOGO

    @property
    def active(self) -> bool:
        return self.configuration.main_open

    def _on_closing(self):
        # self.configuration.main_open = False
        post_event(event_type=RIEventTypes.CLOSE_APP)

    def __init__(self, root: tkinter.Tk, configuration: CompleteConfig, title: str):
        super().__init__(root, title)
        self.relative_setting_btn = None
        self.relative_activation_btn = None
        self.fuel_setting_btn = None
        self.fuel_activation_btn = None
        self.configuration = configuration

        # Stop the app when the main screen is closed
        self.screen.protocol("WM_DELETE_WINDOW", self._on_closing)

        self.spawn_ui_elements()

        self.set_initial_visibility()

    def spawn_ui_elements(self):
        # RacingInsights icon
        logo_img = Image.open("images/RacingInsights_Icon.png")
        logo_img = logo_img.resize((286, 286))
        logo_photo_img = ImageTk.PhotoImage(logo_img)
        logo_label = tkinter.Label(master=self.screen, image=logo_photo_img, bg=self.configuration.bg)
        logo_label.image = logo_photo_img

        # RacingInsights settings icon
        settings_img = Image.open("images/Settings.png")
        settings_img = settings_img.resize((24, 24))
        settings_photo_img = ImageTk.PhotoImage(settings_img)
        # The image needs to be added to a label for it to show in a button... (No need to pack though)
        settings_label = tkinter.Label(master=self.screen, image=settings_photo_img, bg=self.configuration.bg)
        settings_label.image = settings_photo_img

        # -- Fuel buttons row
        fuel_row = tkinter.Frame(self.screen, bg=self.configuration.bg, width=200, height=30)

        # Fuel calculator activation button -> toggles configuration.fuel.active: True/False
        self.fuel_activation_btn = ttk.Button(master=fuel_row,
                                              text="Fuel overlay",
                                              width=self.configuration.button_width,
                                              command=self.toggle_fuel_active)

        # # Fuel settings button
        self.fuel_setting_btn = ttk.Button(master=fuel_row,
                                           image=settings_photo_img,
                                           command=self.open_fuel_settings)

        # -- Relative buttons row
        relative_row = tkinter.Frame(self.screen, bg=self.configuration.bg, width=200, height=30)

        # Relative activation button -> toggles configuration.relative_time.active: True/False
        self.relative_activation_btn = ttk.Button(master=relative_row,
                                                  text="Relative overlay",
                                                  width=self.configuration.button_width,
                                                  command=self.toggle_relative_active)
        # Relative settings button
        self.relative_setting_btn = ttk.Button(master=relative_row,
                                               image=settings_photo_img,
                                               command=self.open_relative_settings)
        # Pack
        logo_label.pack(pady=50, padx=50)
        fuel_row.pack(pady=10)
        self.fuel_activation_btn.pack(pady=5, padx=5, side='left')
        self.fuel_setting_btn.pack(pady=0, padx=5, side='left')

        relative_row.pack(pady=10)
        self.relative_activation_btn.pack(pady=5, padx=5, side='left')
        self.relative_setting_btn.pack(pady=0, padx=5, side='left')

    def toggle_fuel_active(self):
        """
        Method linked to 'Fuel overlay' button press
        """
        # Toggle the setting related to fuel state being active or not
        self.configuration.fuel.active = not self.configuration.fuel.active

    def open_fuel_settings(self):
        """
        Opens the fuel settings and ensures that a fuel overlay is open
        """
        self.configuration.fuel.active = True  # Set state for fuel overlay
        self.configuration.settings.fuel = True  # Set desired state for fuel settings screen
        self.configuration.fuel.locked = False  # Unlock
        post_event(event_type=RIEventTypes.OPEN_FUEL_SETTINGS)

    def toggle_relative_active(self):
        """
        Method linked to 'Relative overlay' button press
        """
        # Toggle the setting related to fuel state being active or not
        self.configuration.relative.active = not self.configuration.relative.active

    def open_relative_settings(self):
        """
        Opens the relative_time settings and ensures that a fuel overlay is open
        """
        self.configuration.relative.active = True  # Set state for relative_time overlay
        self.configuration.settings.relative = True  # Set desired state for relative settings screen
        self.configuration.relative.locked = False  # Unlock
        post_event(event_type=RIEventTypes.OPEN_RELATIVE_SETTINGS)
