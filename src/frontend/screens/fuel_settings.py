import tkinter
from tkinter import ttk

from src.frontend.screen import IconTypes, Screen
from src.frontend.utils.hover_info import HoverInfoWindow
from src.frontend.utils.ri_event_handler import RIEventTypes, post_event, subscribe
from src.startup.my_configuration import CompleteConfig


class FuelSettings(Screen):

    @property
    def icon(self) -> IconTypes:
        return IconTypes.SETTINGS

    @property
    def active(self) -> bool:
        """
        This flag is used as reference to whether the screen should be active/visible or not
        :return:
        """
        return self.configuration.settings.fuel

    def _on_closing(self):
        """
        Determines the behavior when the screen is closed
        :return:
        """
        self.configuration.settings.fuel = False  # Always update the state first
        self.configuration.fuel.locked = True
        self.hide()

    def __init__(self, root: tkinter.Tk, title: str, configuration: CompleteConfig):
        super().__init__(root, title)
        # Indicate which buttons/sliders are available
        self.fuel_checkbutton = None
        self.fuel_var = tkinter.BooleanVar()
        self.last_var = tkinter.BooleanVar()
        self.average_var = tkinter.BooleanVar()
        self.target_var = tkinter.BooleanVar()
        self.range_var = tkinter.BooleanVar()
        self.refuel_var = tkinter.BooleanVar()
        self.finish_var = tkinter.BooleanVar()

        self.lock_button = None
        self.safety_margin_slider = None
        self.text_padding_slider = None
        self.transparency_slider = None
        self.font_size_slider = None

        self.configuration = configuration

        # Spawn UI elements
        self.spawn_ui_elements()

        self.set_initial_visibility()
        # Subscribe to the button generated event
        subscribe(event_type=RIEventTypes.OPEN_FUEL_SETTINGS, fn=self.set_correct_visibility)

    def spawn_ui_elements(self, _=None):
        # Initialize
        font_size_frame = ttk.Frame(master=self.screen,
                                    width=self.configuration.settings.block_width,
                                    height=self.configuration.settings.block_height)

        font_size_label = ttk.Label(master=font_size_frame,
                                    text="Font size",
                                    anchor='center')

        self.font_size_slider = ttk.Scale(master=font_size_frame,
                                          from_=7, to=30,
                                          orient='horizontal',
                                          length=self.configuration.settings.block_width)

        text_padding_frame = ttk.Frame(master=self.screen,
                                       width=self.configuration.settings.block_width,
                                       height=self.configuration.settings.block_height)

        text_padding_label = ttk.Label(master=text_padding_frame,
                                       text="Text padding",
                                       anchor='center')

        self.text_padding_slider = ttk.Scale(master=text_padding_frame,
                                             from_=0, to=25,
                                             orient='horizontal',
                                             length=self.configuration.settings.block_width)

        transparency_frame = ttk.Frame(master=self.screen,
                                       width=self.configuration.settings.block_width,
                                       height=self.configuration.settings.block_height)

        transparency_label = ttk.Label(master=transparency_frame,
                                       text="Transparency",
                                       anchor='center')

        self.transparency_slider = ttk.Scale(master=transparency_frame,
                                             from_=0.6, to=1,
                                             orient='horizontal',
                                             length=self.configuration.settings.block_width)

        safety_margin_frame = ttk.Frame(master=self.screen,
                                        width=self.configuration.settings.block_width,
                                        height=self.configuration.settings.block_height)

        safety_margin_label = ttk.Label(master=safety_margin_frame,
                                        text="Safety margin",
                                        anchor='center')

        self.safety_margin_slider = ttk.Scale(master=safety_margin_frame,
                                              from_=0, to=25,
                                              orient='horizontal',
                                              length=self.configuration.settings.block_width)

        lock_button = ttk.Button(self.screen,
                                 text='Lock/Unlock',
                                 width=self.configuration.button_width,
                                 )

        check_frame = ttk.Frame(master=self.screen,
                                width=self.configuration.settings.block_width,
                                height=self.configuration.settings.block_height)

        fuel_checkbutton = ttk.Checkbutton(master=check_frame,
                                           text="Fuel",
                                           variable=self.fuel_var,
                                           command=self.update_fuel_activated,
                                           onvalue=True,
                                           offvalue=False)

        last_checkbutton = ttk.Checkbutton(master=check_frame,
                                           text="Last",
                                           variable=self.last_var,
                                           command=self.update_last_activated,
                                           onvalue=True,
                                           offvalue=False)

        average_checkbutton = ttk.Checkbutton(master=check_frame,
                                              text="Average",
                                              variable=self.average_var,
                                              command=self.update_average_activated,
                                              onvalue=True,
                                              offvalue=False)

        target_checkbutton = ttk.Checkbutton(master=check_frame,
                                             text="Target",
                                             variable=self.target_var,
                                             command=self.update_target_activated,
                                             onvalue=True,
                                             offvalue=False)

        range_checkbutton = ttk.Checkbutton(master=check_frame,
                                            text="Range",
                                            variable=self.range_var,
                                            command=self.update_range_activated,
                                            onvalue=True,
                                            offvalue=False)

        refuel_checkbutton = ttk.Checkbutton(master=check_frame,
                                             text="Refuel amount",
                                             variable=self.refuel_var,
                                             command=self.update_refuel_activated,
                                             onvalue=True,
                                             offvalue=False)

        finish_checkbutton = ttk.Checkbutton(master=check_frame,
                                             text="Finish target",
                                             variable=self.finish_var,
                                             command=self.update_finish_activated,
                                             onvalue=True,
                                             offvalue=False)

        # Hover info windows
        lock_button_info = HoverInfoWindow(master_widget=lock_button,
                                           text="Locks/Unlocks the fuel overlay for repositioning")

        fuel_info = HoverInfoWindow(master_widget=fuel_checkbutton,
                                    text="Show the live fuel (in liters)")

        last_info = HoverInfoWindow(master_widget=last_checkbutton,
                                    text="Show the fuel consumption of the last lap (in liters)")

        avg_info = HoverInfoWindow(master_widget=average_checkbutton,
                                   text="Show the average (avg) fuel consumption per lap (in liters)")

        target_info = HoverInfoWindow(master_widget=target_checkbutton,
                                      text="Show the fuel consumption target closest to your current average "
                                           "consumption (in liters):"
                                           "\nMaximum fuel usage per lap until the pitstop to do an "
                                           "extra lap on fuel")

        range_info = HoverInfoWindow(master_widget=range_checkbutton,
                                     text="Show the number of laps available on fuel for the average consumption")

        refuel_info = HoverInfoWindow(master_widget=refuel_checkbutton,
                                      text="Show the refuel amount needed to make it to the finish based on your "
                                           "average fuel consumption plus the 'Refuel Margin (%)' (in liters)")

        finish_info = HoverInfoWindow(master_widget=finish_checkbutton,
                                      text="Show the maximum fuel usage per lap needed (from now until the finish) to "
                                           "make it to the finish without refueling (in liters)")

        # Set
        self.font_size_slider.set(value=self.configuration.fuel.font_size)
        self.text_padding_slider.set(value=self.configuration.fuel.text_padding)
        self.transparency_slider.set(value=self.configuration.fuel.transparency)
        self.safety_margin_slider.set(value=self.configuration.fuel.safety_margin)

        self.fuel_var.set(value=self.configuration.fuel.fuel_activated)
        self.last_var.set(value=self.configuration.fuel.last_activated)
        self.average_var.set(value=self.configuration.fuel.avg_activated)
        self.target_var.set(value=self.configuration.fuel.target_activated)
        self.range_var.set(value=self.configuration.fuel.range_activated)
        self.refuel_var.set(value=self.configuration.fuel.refuel_activated)
        self.finish_var.set(value=self.configuration.fuel.finish_activated)

        # Pack
        font_size_frame.pack(pady=10)
        font_size_label.pack(fill='both', pady=10)
        self.font_size_slider.pack(padx=5)

        text_padding_frame.pack(pady=10)
        text_padding_label.pack(fill='both', pady=10)
        self.text_padding_slider.pack(padx=5)

        transparency_frame.pack(pady=10)
        transparency_label.pack(fill='both', pady=10)
        self.transparency_slider.pack(padx=5)

        safety_margin_frame.pack(pady=10)
        safety_margin_label.pack(fill='both', pady=10)
        self.safety_margin_slider.pack(padx=5)

        lock_button.pack(pady=10, padx=50)

        check_frame.pack(pady=5)

        fuel_checkbutton.pack(pady=5, fill='both', anchor='nw')
        last_checkbutton.pack(pady=5, fill='both', anchor='nw')
        average_checkbutton.pack(pady=5, fill='both', anchor='nw')
        target_checkbutton.pack(pady=5, fill='both', anchor='nw')
        range_checkbutton.pack(pady=5, fill='both', anchor='nw')
        refuel_checkbutton.pack(pady=5, fill='both', anchor='nw')
        finish_checkbutton.pack(pady=5, fill='both', anchor='nw')

        # Bind
        self.font_size_slider.bind("<ButtonRelease-1>", self.update_font_size)
        self.text_padding_slider.bind("<ButtonRelease-1>", self.update_text_padding)
        self.transparency_slider.bind("<ButtonRelease-1>", self.update_transparency)
        self.safety_margin_slider.bind("<ButtonRelease-1>", self.update_safety_margin)
        lock_button.configure(command=self.update_lock_state)

    def update_font_size(self, event_data=None):
        self.configuration.fuel.font_size = int(self.font_size_slider.get())
        post_event(event_type=RIEventTypes.FUEL_FEATURE_CHANGE)

    def update_text_padding(self, event_data=None):
        self.configuration.fuel.text_padding = int(self.text_padding_slider.get())
        post_event(event_type=RIEventTypes.FUEL_FEATURE_CHANGE)

    def update_transparency(self, event_data=None):
        self.configuration.fuel.transparency = float(self.transparency_slider.get())

    def update_safety_margin(self, event_data=None):
        self.configuration.fuel.safety_margin = float(self.safety_margin_slider.get())

    def update_lock_state(self, event_data=None):
        self.configuration.fuel.locked = not self.configuration.fuel.locked

    def update_fuel_activated(self):
        self.configuration.fuel.fuel_activated = self.fuel_var.get()

    def update_last_activated(self):
        self.configuration.fuel.last_activated = self.last_var.get()

    def update_average_activated(self):
        self.configuration.fuel.avg_activated = self.average_var.get()

    def update_target_activated(self):
        self.configuration.fuel.target_activated = self.target_var.get()

    def update_range_activated(self):
        self.configuration.fuel.range_activated = self.range_var.get()

    def update_refuel_activated(self):
        self.configuration.fuel.refuel_activated = self.refuel_var.get()

    def update_finish_activated(self):
        self.configuration.fuel.finish_activated = self.finish_var.get()
