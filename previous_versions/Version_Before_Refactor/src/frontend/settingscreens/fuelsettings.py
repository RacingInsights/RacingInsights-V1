import tkinter
from tkinter import ttk

from previous_versions.Version_Before_Refactor.src.frontend.hover_info import HoverInfoWindow
from previous_versions.Version_Before_Refactor.src.frontend.settingscreens.settingscreen_abstract import SettingScreenAbstract, SettingsCheckButton


class FuelSettingsScreen(SettingScreenAbstract):
    def __init__(self, parent_obj, config_data, linked_app, cfg_key):
        super().__init__(parent_obj, config_data, linked_app, cfg_key)

        # Initialize the widgets
        self.fontsize_frame = ttk.Frame(self.master, width=self.cfg.block_width, height=self.cfg.block_height)
        self.fontsize_frame.pack(pady=10)

        self.fontsize_label = ttk.Label(self.fontsize_frame, text="Font size", anchor='center')
        self.fontsize_label.pack(fill='both', pady=10)
        self.fontsize_slider = ttk.Scale(self.fontsize_frame, from_=7, to=30, orient='horizontal',
                                         length=self.cfg.block_width)
        self.fontsize_slider.bind("<ButtonRelease-1>", self.update_fontsize)

        self.fontsize_slider.set(self.parent_obj.fuel_app.cfg.font_size)
        self.fontsize_slider.pack(padx=5)


        self.textpadding_frame = ttk.Frame(self.master, width=self.cfg.block_width, height=self.cfg.block_height)
        self.textpadding_frame.pack(pady=10)

        self.textpadding_label = ttk.Label(self.textpadding_frame, text="Text padding", anchor='center')
        self.textpadding_label.pack(fill='both', pady=10)
        self.textpadding_slider = ttk.Scale(self.textpadding_frame, from_=0, to=25, orient='horizontal',
                                            length=self.cfg.block_width)
        self.textpadding_slider.bind("<ButtonRelease-1>", self.update_textpadding)
        self.textpadding_slider.set(self.parent_obj.fuel_app.cfg.text_padding)
        self.textpadding_slider.pack(padx=5)

        self.safety_margin_text_var = tkinter.StringVar()
        self.safety_margin_text_var.set(f"{self.parent_obj.fuel_app.cfg.safety_margin:.2f}")

        self.safety_margin_frame = ttk.Frame(self.master, width=self.cfg.block_width, height=self.cfg.block_height)
        self.safety_margin_frame.pack(pady=10)

        self.safety_margin_hover_info = HoverInfoWindow(master_widget=self.safety_margin_frame,
                                                        text="Set the safety margin to be included in the refuel calculation"
                                                             "\nUseful to set this higher when fuel saving only before the pitstop")

        self.safety_margin_label = ttk.Label(self.safety_margin_frame, text="Refuel margin (%)",
                                             anchor='center')
        self.safety_margin_label.pack(fill='both', pady=10)
        self.safety_margin_slider = ttk.Scale(self.safety_margin_frame, from_=0, to=15, orient='horizontal',
                                             length=self.cfg.block_width)
        self.safety_margin_slider.bind("<ButtonRelease-1>",self.update_safety_margin)

        self.safety_margin_slider.set(self.parent_obj.fuel_app.cfg.safety_margin)
        self.safety_margin_slider.pack(padx=5)

        self.safety_margin_value_label = ttk.Label(self.safety_margin_frame, textvariable=self.safety_margin_text_var,
                                                   anchor='center')
        self.safety_margin_value_label.pack(fill='both', pady=10)

        self.open_on_startup_frame = ttk.Frame(self.master, width=self.cfg.block_width, height=self.cfg.block_height)
        self.open_on_startup_frame.pack(pady=10)

        self.open_on_startup_checkbutton = SettingsCheckButton(master=self.open_on_startup_frame, cfg=self.cfg,
                                                               parent_obj=self.parent_obj,
                                                               name="Open on startup",
                                                               setting_name="fuel_open_on_startup",
                                                               linked_app=self.parent_obj)

        self.lockbutton = ttk.Button(self.master, text='Lock/Unlock', width=self.cfg.button_width,
                                     command=self.toggle_app_lock)
        self.lockbutton.pack(pady=10)

        # Add a hover info window to explain the button's functionality
        self.lockbutton_hover_info = HoverInfoWindow(master_widget=self.lockbutton,
                                                     text="Locks/Unlocks the fuel overlay for repositioning")

        self.check_frame = ttk.Frame(master=self.master, width=self.cfg.block_width, height=self.cfg.block_height)
        self.check_frame.pack(pady=10)

        self.fuel_checkbutton = SettingsCheckButton(master=self.check_frame, cfg=self.cfg, parent_obj=self.parent_obj,
                                                    name="Fuel",
                                                    setting_name="fuel_activated",
                                                    linked_app=self.app)

        self.last_checkbutton = SettingsCheckButton(master=self.check_frame, cfg=self.cfg, parent_obj=self.parent_obj,
                                                    name="Last",
                                                    setting_name="last_activated",
                                                    linked_app=self.app)

        self.avg_checkbutton = SettingsCheckButton(master=self.check_frame, cfg=self.cfg, parent_obj=self.parent_obj,
                                                   name="Avg",
                                                   setting_name="avg_activated",
                                                   linked_app=self.app)

        self.target_checkbutton = SettingsCheckButton(master=self.check_frame, cfg=self.cfg, parent_obj=self.parent_obj,
                                                      name="Target", setting_name="target_activated",
                                                      linked_app=self.app)

        self.range_checkbutton = SettingsCheckButton(master=self.check_frame, cfg=self.cfg, parent_obj=self.parent_obj,
                                                     name="Range", setting_name="range_activated",
                                                     linked_app=self.app)

        self.refuel_checkbutton = SettingsCheckButton(master=self.check_frame, cfg=self.cfg, parent_obj=self.parent_obj,
                                                      name="Refuel", setting_name="refuel_activated",
                                                      linked_app=self.app)

        self.finish_checkbutton = SettingsCheckButton(master=self.check_frame, cfg=self.cfg, parent_obj=self.parent_obj,
                                                      name="Finish", setting_name="finish_activated",
                                                      linked_app=self.app)

        self.remaining_checkbutton = SettingsCheckButton(master=self.check_frame, cfg=self.cfg,
                                                         parent_obj=self.parent_obj,
                                                         name="Remaining", setting_name="remaining_activated",
                                                         linked_app=self.app)

        self.fuel_checkbutton_hover_info = HoverInfoWindow(master_widget=self.fuel_checkbutton.checkbutton_frame,
                                                           text="Show the live fuel (in liters)")
        self.last_checkbutton_hover_info = HoverInfoWindow(master_widget=self.last_checkbutton.checkbutton_frame,
                                                           text="Show the fuel consumption of the last lap (in liters)")
        self.avg_checkbutton_hover_info = HoverInfoWindow(master_widget=self.avg_checkbutton.checkbutton_frame,
                                                          text="Show the average (avg) fuel consumption per lap (in liters)")
        self.target_checkbutton_hover_info = HoverInfoWindow(master_widget=self.target_checkbutton.checkbutton_frame,
                                                             text="Show the 2 fuel consumption targets closest to your current average consumption (in liters)"
                                                                  "\nUpper target: maximum fuel usage per lap until the pitstop to do the same number of laps as with current average"
                                                                  "\nLower target: maximum fuel usage per lap until the pitstop to do an extra lap on fuel")
        self.range_checkbutton_hover_info = HoverInfoWindow(master_widget=self.range_checkbutton.checkbutton_frame,
                                                            text="Show the number of laps available on fuel for the Upper and Lower Target")
        self.refuel_checkbutton_hover_info = HoverInfoWindow(master_widget=self.refuel_checkbutton.checkbutton_frame,
                                                             text="Show the refuel amount needed to make it to the finish based on your average fuel consumption plus the 'Refuel Margin (%)' (in liters)")
        self.finish_checkbutton_hover_info = HoverInfoWindow(master_widget=self.finish_checkbutton.checkbutton_frame,
                                                             text="Show the maximum fuel usage per lap needed (from now until the finish) to make it to the finish without refueling (in liters)")
        self.remaining_checkbutton_hover_info = HoverInfoWindow(
            master_widget=self.remaining_checkbutton.checkbutton_frame,
            text="Show the number of laps to go until the finish")

    def update_fontsize(self, _):
        value = self.fontsize_slider.get()
        font_size = int(float(value))
        self.app.update_cfg_value(setting="font_size", value=font_size)
        self.app.update_appearance()

    def update_textpadding(self, _):
        value = self.textpadding_slider.get()
        font_size = int(float(value))
        self.app.update_cfg_value(setting="text_padding", value=font_size)
        self.app.update_appearance()

    def update_safety_margin(self, _):
        value = self.safety_margin_slider.get()
        safety_margin = float(value)
        self.safety_margin_text_var.set(f"{safety_margin:.2f}")
        self.app.update_cfg_value(setting="safety_margin", value=safety_margin)
        self.app.update_appearance()
