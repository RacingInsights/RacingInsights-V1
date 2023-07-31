# hide_pits -> Checkutton

from tkinter import ttk

from previous_versions.Version_Before_Refactor.src.frontend.hover_info import HoverInfoWindow
from previous_versions.Version_Before_Refactor.src.frontend.settingscreens.settingscreen_abstract import SettingScreenAbstract, SettingsCheckButton


class RelativeSettingsScreen(SettingScreenAbstract):
    def __init__(self, parent_obj, config_data, linked_app, cfg_key):
        super().__init__(parent_obj, config_data, linked_app, cfg_key)

        self.fontsize_frame = ttk.Frame(self.master, width=self.cfg.block_width, height=self.cfg.block_height)
        self.fontsize_frame.pack(pady=10)

        self.fontsize_label = ttk.Label(self.fontsize_frame, text="Font size", anchor='center')
        self.fontsize_label.pack(fill='both', pady=10)
        self.fontsize_slider = ttk.Scale(self.fontsize_frame, from_=7, to=30, orient='horizontal',
                                         length=self.cfg.block_width)
        self.fontsize_slider.bind("<ButtonRelease-1>", self.update_fontsize)
        self.fontsize_slider.set(self.app.cfg.font_size)
        self.fontsize_slider.pack(padx=5)

        self.textpadding_x_frame = ttk.Frame(self.master, width=self.cfg.block_width, height=self.cfg.block_height)
        self.textpadding_x_frame.pack(pady=10)

        self.textpadding_x_label = ttk.Label(self.textpadding_x_frame, text="Horizontal padding", anchor='center')
        self.textpadding_x_label.pack(fill='both', pady=10)
        self.textpadding_x_slider = ttk.Scale(self.textpadding_x_frame, from_=0, to=25, orient='horizontal',
                                              length=self.cfg.block_width)
        self.textpadding_x_slider.bind("<ButtonRelease-1>", self.update_textpadding_x)

        self.textpadding_x_slider.set(self.app.cfg.text_padding_x)
        self.textpadding_x_slider.pack(padx=5)

        self.textpadding_y_frame = ttk.Frame(self.master, width=self.cfg.block_width, height=self.cfg.block_height)
        self.textpadding_y_frame.pack(pady=10)

        self.textpadding_y_label = ttk.Label(self.textpadding_y_frame, text="Vertical padding", anchor='center')
        self.textpadding_y_label.pack(fill='both', pady=10)
        self.textpadding_y_slider = ttk.Scale(self.textpadding_y_frame, from_=0, to=15, orient='horizontal',
                                              length=self.cfg.block_width)

        self.textpadding_y_slider.bind("<ButtonRelease-1>", self.update_textpadding_y)

        self.textpadding_y_slider.set(self.app.cfg.text_padding_y)
        self.textpadding_y_slider.pack(padx=5)

        self.open_on_startup_frame = ttk.Frame(self.master, width=self.cfg.block_width, height=self.cfg.block_height)
        self.open_on_startup_frame.pack(pady=10)

        self.open_on_startup_checkbutton = SettingsCheckButton(master=self.open_on_startup_frame, cfg=self.cfg,
                                                               parent_obj=self.parent_obj,
                                                               name="Open on startup",
                                                               setting_name="relative_open_on_startup",
                                                               linked_app=self.parent_obj)

        self.lockbutton = ttk.Button(self.master, text='Lock/Unlock', width=self.cfg.button_width,
                                     command=self.toggle_app_lock)
        self.lockbutton.pack(pady=10)

        # Add a hover info window to explain the button's functionality
        self.lockbutton_hover_info = HoverInfoWindow(master_widget=self.lockbutton,
                                                     text="Locks/Unlocks the relative overlay for repositioning")

        self.check_frame = ttk.Frame(master=self.master, width=self.cfg.block_width, height=self.cfg.block_height)
        self.check_frame.pack(pady=10)

        self.hide_pits_checkbutton = SettingsCheckButton(master=self.check_frame, cfg=self.cfg,
                                                         parent_obj=self.parent_obj,
                                                         name="Hide cars in pits",
                                                         setting_name="hide_pits",
                                                         linked_app=self.app)

        self.driver_license_checkbutton = SettingsCheckButton(master=self.check_frame, cfg=self.cfg,
                                                              parent_obj=self.parent_obj,
                                                              name="Driver license",
                                                              setting_name="license_activated",
                                                              linked_app=self.app)

        self.irating_checkbutton = SettingsCheckButton(master=self.check_frame, cfg=self.cfg,
                                                       parent_obj=self.parent_obj,
                                                       name="iRating",
                                                       setting_name="irating_activated",
                                                       linked_app=self.app)

    def update_fontsize(self, _):
        value = self.fontsize_slider.get()
        font_size = int(float(value))
        self.app.update_cfg_value(setting="font_size", value=font_size)
        self.app.update_appearance()

    def update_textpadding_x(self, _):
        value = self.textpadding_x_slider.get()
        text_padding_x = int(float(value))
        self.app.update_cfg_value(setting="text_padding_x", value=text_padding_x)
        self.app.update_appearance()

    def update_textpadding_y(self, _):
        value = self.textpadding_y_slider.get()
        text_padding_y = int(float(value))
        self.app.update_cfg_value(setting="text_padding_y", value=text_padding_y)
        self.app.update_appearance()
