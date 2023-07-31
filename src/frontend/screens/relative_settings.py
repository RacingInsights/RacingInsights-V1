import tkinter
from tkinter import ttk

from src.frontend.screen import IconTypes, Screen
from src.frontend.utils.ri_event_handler import RIEventTypes, post_event, subscribe
from src.startup.my_configuration import CompleteConfig


class RelativeSettings(Screen):

    @property
    def icon(self) -> IconTypes:
        return IconTypes.SETTINGS

    @property
    def active(self) -> bool:
        """
        This flag is used as reference to whether the screen should be active/visible or not
        :return:
        """
        return self.configuration.settings.relative

    def _on_closing(self):
        """
        Determines the behavior when the screen is closed
        :return:
        """
        self.configuration.settings.relative = False  # Always update the state first
        self.configuration.relative.locked = True
        self.hide()

    def __init__(self, root: tkinter.Tk, title: str, configuration: CompleteConfig):
        super().__init__(root, title)
        self.license_activated_var = tkinter.BooleanVar()
        self.irating_activated_var = tkinter.BooleanVar()
        self.hide_pits_var = tkinter.BooleanVar()

        self.name_width_slider = None
        self.transparency_slider = None
        self.padding_y_slider = None
        self.padding_x_slider = None
        self.font_size_slider = None

        self.configuration = configuration
        self.spawn_ui_elements()
        self.set_initial_visibility()

        # Subscribe to the button generated event
        subscribe(event_type=RIEventTypes.OPEN_RELATIVE_SETTINGS, fn=self.set_correct_visibility)

    def spawn_ui_elements(self):
        # Initialize
        font_size_frame = ttk.Frame(master=self.screen,
                                    width=self.configuration.settings.block_width,
                                    height=self.configuration.settings.block_height)

        font_size_label = ttk.Label(master=font_size_frame,
                                    text="Font size",
                                    anchor='center')

        self.font_size_slider = ttk.Scale(master=font_size_frame,
                                          from_=6, to=20,
                                          orient='horizontal',
                                          length=self.configuration.settings.block_width)

        padding_x_frame = ttk.Frame(master=self.screen,
                                    width=self.configuration.settings.block_width,
                                    height=self.configuration.settings.block_height)

        padding_x_label = ttk.Label(master=padding_x_frame,
                                    text="Padding x",
                                    anchor='center')

        self.padding_x_slider = ttk.Scale(master=padding_x_frame,
                                          from_=0, to=8,
                                          orient='horizontal',
                                          length=self.configuration.settings.block_width)

        padding_y_frame = ttk.Frame(master=self.screen,
                                    width=self.configuration.settings.block_width,
                                    height=self.configuration.settings.block_height)

        padding_y_label = ttk.Label(master=padding_y_frame,
                                    text="Padding y",
                                    anchor='center')

        self.padding_y_slider = ttk.Scale(master=padding_y_frame,
                                          from_=0, to=8,
                                          orient='horizontal',
                                          length=self.configuration.settings.block_width)

        name_width_frame = ttk.Frame(master=self.screen,
                                     width=self.configuration.settings.block_width,
                                     height=self.configuration.settings.block_height)

        name_width_label = ttk.Label(master=name_width_frame,
                                     text="Driver name width",
                                     anchor='center')

        self.name_width_slider = ttk.Scale(master=name_width_frame,
                                           from_=5, to=20,
                                           orient='horizontal',
                                           length=self.configuration.settings.block_width)

        nr_rows_frame = ttk.Frame(master=self.screen,
                                  width=self.configuration.settings.block_width,
                                  height=self.configuration.settings.block_height)

        nr_rows_label = ttk.Label(master=nr_rows_frame,
                                  text="# drivers",
                                  anchor='center')

        self.nr_rows_slider = ttk.Scale(master=nr_rows_frame,
                                        from_=2, to=9,  # should match MAX_DRIVERS in relative overlay
                                        orient='horizontal',
                                        length=self.configuration.settings.block_width)

        transparency_frame = ttk.Frame(master=self.screen,
                                       width=self.configuration.settings.block_width,
                                       height=self.configuration.settings.block_height)

        nr_rows_front_frame = ttk.Frame(master=self.screen,
                                        width=self.configuration.settings.block_width,
                                        height=self.configuration.settings.block_height)

        nr_rows_front_label = ttk.Label(master=nr_rows_front_frame,
                                        text="# drivers ahead",
                                        anchor='center')

        self.nr_rows_front_slider = ttk.Scale(master=nr_rows_front_frame,
                                              from_=0, to=8,
                                              orient='horizontal',
                                              length=self.configuration.settings.block_width)

        transparency_label = ttk.Label(master=transparency_frame,
                                       text="Transparency",
                                       anchor='center')

        self.transparency_slider = ttk.Scale(master=transparency_frame,
                                             from_=0.6, to=1,
                                             orient='horizontal',
                                             length=self.configuration.settings.block_width)

        lock_button = ttk.Button(self.screen,
                                 text='Lock/Unlock',
                                 width=self.configuration.button_width,
                                 )

        check_frame = ttk.Frame(master=self.screen,
                                width=self.configuration.settings.block_width,
                                height=self.configuration.settings.block_height)

        hide_pits_checkbutton = ttk.Checkbutton(master=check_frame,
                                                text="Hide pits",
                                                variable=self.hide_pits_var,
                                                command=self.update_hide_pits,
                                                onvalue=True,
                                                offvalue=False)

        irating_activated_checkbutton = ttk.Checkbutton(master=check_frame,
                                                        text="Show irating",
                                                        variable=self.irating_activated_var,
                                                        command=self.update_irating_activated,
                                                        onvalue=True,
                                                        offvalue=False)

        license_activated_checkbutton = ttk.Checkbutton(master=check_frame,
                                                        text="Show license",
                                                        variable=self.license_activated_var,
                                                        command=self.update_license_activated,
                                                        onvalue=True,
                                                        offvalue=False)

        # Set
        self.name_width_slider.set(value=self.configuration.relative.driver_name_width)
        self.transparency_slider.set(value=self.configuration.relative.transparency)
        self.padding_y_slider.set(value=self.configuration.relative.text_padding_y)
        self.padding_x_slider.set(value=self.configuration.relative.text_padding_x)
        self.font_size_slider.set(value=self.configuration.relative.font_size)
        self.nr_rows_slider.set(value=self.configuration.relative.nr_rows)
        self.nr_rows_front_slider.set(value=self.configuration.relative.nr_rows_front)

        self.hide_pits_var.set(value=self.configuration.relative.hide_pits)
        self.license_activated_var.set(value=self.configuration.relative.license_activated)
        self.irating_activated_var.set(value=self.configuration.relative.irating_activated)

        # Pack
        font_size_frame.pack(pady=10)
        font_size_label.pack(fill='both', pady=10)
        self.font_size_slider.pack(padx=5)

        padding_x_frame.pack(pady=10)
        padding_x_label.pack(fill='both', pady=10)
        self.padding_x_slider.pack(padx=5)

        padding_y_frame.pack(pady=10)
        padding_y_label.pack(fill='both', pady=10)
        self.padding_y_slider.pack(padx=5)

        transparency_frame.pack(pady=10)
        transparency_label.pack(fill='both', pady=10)
        self.transparency_slider.pack(padx=5)

        name_width_frame.pack(pady=10)
        name_width_label.pack(fill='both', pady=10)
        self.name_width_slider.pack(padx=5)

        nr_rows_frame.pack(pady=10)
        nr_rows_label.pack(fill='both', pady=10)
        self.nr_rows_slider.pack(padx=5)

        nr_rows_front_frame.pack(pady=10)
        nr_rows_front_label.pack(fill='both', pady=10)
        self.nr_rows_front_slider.pack(padx=5)

        lock_button.pack(pady=10, padx=50)

        check_frame.pack(pady=5)

        hide_pits_checkbutton.pack(pady=5, fill='both', anchor='nw')
        license_activated_checkbutton.pack(pady=5, fill='both', anchor='nw')
        irating_activated_checkbutton.pack(pady=5, fill='both', anchor='nw')

        # Bind
        self.name_width_slider.bind("<ButtonRelease-1>", self.update_name_width)
        self.transparency_slider.bind("<ButtonRelease-1>", self.update_transparency)
        self.padding_y_slider.bind("<ButtonRelease-1>", self.update_padding_y)
        self.padding_x_slider.bind("<ButtonRelease-1>", self.update_padding_x)
        self.font_size_slider.bind("<ButtonRelease-1>", self.update_font_size)
        self.nr_rows_slider.bind("<ButtonRelease-1>", self.update_nr_rows)
        self.nr_rows_front_slider.bind("<ButtonRelease-1>", self.update_nr_rows_front)

        lock_button.configure(command=self.update_lock_state)

    def update_name_width(self, _):
        self.configuration.relative.driver_name_width = int(self.name_width_slider.get())
        post_event(event_type=RIEventTypes.RELATIVE_FEATURE_CHANGE)

    def update_transparency(self, _):
        self.configuration.relative.transparency = float(self.transparency_slider.get())
        post_event(event_type=RIEventTypes.RELATIVE_FEATURE_CHANGE)

    def update_padding_x(self, _):
        self.configuration.relative.text_padding_x = int(self.padding_x_slider.get())
        post_event(event_type=RIEventTypes.RELATIVE_FEATURE_CHANGE)
        post_event(event_type=RIEventTypes.RELATIVE_FEATURE_CHANGE)  # Twice, to avoid not going to 0 on first update

    def update_padding_y(self, _):
        self.configuration.relative.text_padding_y = int(self.padding_y_slider.get())
        post_event(event_type=RIEventTypes.RELATIVE_FEATURE_CHANGE)

    def update_nr_rows(self, _):
        self.configuration.relative.nr_rows = int(self.nr_rows_slider.get())
        post_event(event_type=RIEventTypes.RELATIVE_FEATURE_CHANGE)
        if self.configuration.relative.nr_rows_front > self.configuration.relative.nr_rows:
            self.configuration.relative.nr_rows_front = self.configuration.relative.nr_rows - 1
            self.nr_rows_front_slider.set(self.configuration.relative.nr_rows_front)

    def update_nr_rows_front(self, _):
        self.configuration.relative.nr_rows_front = int(self.nr_rows_front_slider.get())
        if self.configuration.relative.nr_rows_front > self.configuration.relative.nr_rows:
            self.configuration.relative.nr_rows_front = self.configuration.relative.nr_rows - 1
            self.nr_rows_front_slider.set(self.configuration.relative.nr_rows_front)
        post_event(event_type=RIEventTypes.RELATIVE_FEATURE_CHANGE)

    def update_font_size(self, _):
        self.configuration.relative.font_size = int(self.font_size_slider.get())
        post_event(event_type=RIEventTypes.RELATIVE_FEATURE_CHANGE)

    def update_license_activated(self):
        self.configuration.relative.license_activated = self.license_activated_var.get()
        post_event(event_type=RIEventTypes.RELATIVE_FEATURE_CHANGE)

    def update_irating_activated(self):
        self.configuration.relative.irating_activated = self.irating_activated_var.get()
        post_event(event_type=RIEventTypes.RELATIVE_FEATURE_CHANGE)

    def update_hide_pits(self):
        self.configuration.relative.hide_pits = self.hide_pits_var.get()

    def update_lock_state(self, event_data=None):
        self.configuration.relative.locked = not self.configuration.relative.locked
