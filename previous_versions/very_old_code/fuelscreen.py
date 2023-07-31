import threading
import time
import tkinter
from tkinter import ttk

from src.backend.iRacing.state import State
from src.backend.iRacing.telemetry import Telemetry
from src.frontend.overlays.overlay_abstract import OverlayAbstract


class FuelScreen(OverlayAbstract):
    def __init__(self, parent_obj, telemetry: Telemetry, state: State, config_data, rounded=True):
        super().__init__(parent_obj, rounded, overlay_type="fuel", config_data=config_data)

        self.set_styling_vars()

        self.fuelvar = tkinter.StringVar()
        self.fuelvar.set("000.00")
        self.lastvar = tkinter.StringVar()
        self.lastvar.set("00.00")
        self.avgvar = tkinter.StringVar()
        self.avgvar.set("00.00")
        self.targetcurrentvar = tkinter.StringVar()
        self.targetcurrentvar.set("00.00")
        self.targetextravar = tkinter.StringVar()
        self.targetextravar.set("00.00")
        self.rangevar = tkinter.StringVar()
        self.rangevar.set("00.00")
        self.rangeextravar = tkinter.StringVar()
        self.rangeextravar.set("00.00")
        self.refuelvar = tkinter.StringVar()
        self.refuelvar.set("000.00")

        self.init_visuals()

        # Create a thread for updating the dashboard -> Alternative, use events instead?
        # Set this thread to be a daemon, this way the application will close when all non-daemon threads are closed
        # (the only non-daemonic thread should be the main thread for this functionality)
        thread = threading.Thread(target=self.update_dash, args=[telemetry, state])
        thread.daemon = True
        thread.start()

    def set_styling_vars(self):
        """
        sets the variables that are dependent on input (=settings) variables
        font, block width, block height, block sub height
        :return:
        """
        self.font = f'{self.cfg.font_style} {self.cfg.font_size} {self.cfg.font_extra}'

        # Automatically calculate the block dimensions with font size and text padding as customizable settings
        self.block_width = int(self.cfg.font_size * 4.5 + self.cfg.text_padding)
        self.block_height = int(self.cfg.font_size * 5 + self.cfg.text_padding)
        self.block_sub_height = int(self.block_height / 3)

        # Calculate the value of the lower sub block to prevent 1 pixel offset due to mod(block_height,3) NOT being a natural number (N)
        self.block_sub_height_last = self.block_height - 2 * self.block_sub_height

    def update_dash(self, tm: Telemetry, state: State):
        """
        Loop that updates the frontend (dashboard) based on the data it gets from the backend (iRacing telemetry).
        Note that this function is supposed to be called in a different thread than the main
        :param tm:
        :param state:
        :return:
        """
        while True:
            # Update the frontend if still connected
            if state.ir_connected:
                self.fuelvar.set(f"{tm.fuel:.2f}")
                self.lastvar.set(f"{tm.cons:.2f}")
                self.avgvar.set(f"{tm.avg_cons:.2f}")
                self.targetcurrentvar.set(f"{tm.target_cons_current:.2f}")
                self.targetextravar.set(f"{tm.target_cons_extra:.2f}")
                self.rangevar.set(f"{tm.laps_left_current}")
                self.rangeextravar.set(f"{tm.laps_left_extra}")
                self.refuelvar.set(f"{tm.refuel:.2f}")

            time.sleep(1)

    def respawn_visuals(self):
        self.set_styling_vars()

        # Clear all the previous frames that are available
        list_of_attributes = ['fuel_frame', 'last_frame', 'avg_frame', 'target_frame', 'range_frame', 'refuel_frame']
        for frame_name in list_of_attributes:
            if hasattr(self, frame_name):
                self.clear_frame(getattr(self, frame_name))

        self.init_visuals()

    def resize_text(self, font_size):
        self.cfg.font_size = font_size
        self.respawn_visuals()

    def resize_padding(self, text_padding):
        self.cfg.text_padding = text_padding
        self.respawn_visuals()

    def clear_frame(self, frame: tkinter.Frame):
        frame.grid_forget()
        for widgets in frame.winfo_children():
            widgets.destroy()

    def init_visuals(self):
        """
        Adds the visual elements of the fuel overlay
        :return:
        """
        if self.cfg.fuel_activated:
            self.fuel_frame = ttk.Frame(self.master, width=self.block_width, height=self.block_height)
            self.fuel_frame.grid(row=0, column=0)
            self.fuel_frame.grid_propagate(False)

            self.fuelheader = tkinter.Label(self.fuel_frame, text="Fuel", font=self.font, fg=self.cfg.fg_color_header)
            self.fuelheader.place(relx=0.5, rely=0.165, anchor='center')

            self.fuellabel = tkinter.Label(self.fuel_frame, textvariable=self.fuelvar, font=self.font,
                                           fg=self.cfg.fg_color_values)
            self.fuellabel.place(relx=0.5, rely=0.66, anchor='center')

        if self.cfg.last_activated:
            self.last_frame = ttk.Frame(self.overlay_frame, width=self.block_width, height=self.block_height)
            self.last_frame.grid(row=0, column=1)
            self.last_frame.grid_propagate(False)

            self.lastheader = tkinter.Label(self.last_frame, text="Last", font=self.font, fg=self.cfg.fg_color_header)
            self.lastheader.place(relx=0.5, rely=0.165, anchor='center')

            self.lastlabel = tkinter.Label(self.last_frame, textvariable=self.lastvar, font=self.font,
                                           fg=self.cfg.fg_color_values)
            self.lastlabel.place(relx=0.5, rely=0.66, anchor='center')

        if self.cfg.avg_activated:
            self.avg_frame = ttk.Frame(self.overlay_frame, width=self.block_width, height=self.block_height)
            self.avg_frame.grid(row=0, column=2)
            self.avg_frame.grid_propagate(False)

            self.avgheader = tkinter.Label(self.avg_frame, text="Avg", font=self.font, fg=self.cfg.fg_color_header)
            self.avgheader.place(relx=0.5, rely=0.165, anchor='center')

            self.avglabel = tkinter.Label(self.avg_frame, textvariable=self.avgvar, font=self.font,
                                          fg=self.cfg.fg_color_values)
            self.avglabel.place(relx=0.5, rely=0.66, anchor='center')

        if self.cfg.target_activated:
            self.target_frame = ttk.Frame(self.overlay_frame, width=self.block_width, height=self.block_height)
            self.target_frame.grid(row=0, column=3)
            self.target_frame.grid_propagate(False)

            self.target_header_frame = ttk.Frame(self.target_frame, width=self.block_width,
                                                 height=self.block_sub_height)
            self.target_header_frame.grid(row=0, column=0)
            self.target_header_frame.grid_propagate(False)

            self.target_current_frame = ttk.Frame(self.target_frame, width=self.block_width,
                                                  height=self.block_sub_height)
            self.target_current_frame.grid(row=1, column=0)
            self.target_current_frame.grid_propagate(False)

            self.target_extra_frame = ttk.Frame(self.target_frame, width=self.block_width,
                                                height=self.block_sub_height_last)
            self.target_extra_frame.grid(row=2, column=0)
            self.target_extra_frame.grid_propagate(False)

            self.targetheader = tkinter.Label(self.target_frame,
                                              text="Target",
                                              font=self.font,
                                              fg=self.cfg.fg_color_header)
            self.targetheader.place(relx=0.5, rely=0.165, anchor='center')

            self.targetcurrentlabel = tkinter.Label(self.target_current_frame, textvariable=self.targetcurrentvar,
                                                    font=self.font, fg=self.cfg.fg_color_values)
            self.targetcurrentlabel.place(relx=0.5, rely=0.5, anchor='center')

            self.targetextralabel = tkinter.Label(self.target_extra_frame,
                                                  textvariable=self.targetextravar,
                                                  font=self.font,
                                                  fg=self.cfg.fg_color_special)
            self.targetextralabel.place(relx=0.5, rely=0.5, anchor='center')

        if self.cfg.range_activated:
            self.range_frame = ttk.Frame(self.overlay_frame, width=self.block_width, height=self.block_height)
            self.range_frame.grid(row=0, column=4)
            self.range_frame.grid_propagate(False)

            # Laps frame is divided in 3 sub-frames (2 values + 1 header)
            self.range_header_frame = ttk.Frame(self.range_frame, width=self.block_width,
                                                height=self.block_sub_height)
            self.range_header_frame.grid(row=0, column=0)
            self.range_header_frame.grid_propagate(False)

            self.range_current_frame = ttk.Frame(self.range_frame, width=self.block_width,
                                                 height=self.block_sub_height)
            self.range_current_frame.grid(row=1, column=0)
            self.range_current_frame.grid_propagate(False)

            self.range_extra_frame = ttk.Frame(self.range_frame, width=self.block_width,
                                               height=self.block_sub_height_last)
            self.range_extra_frame.grid(row=2, column=0, sticky='SE', pady=0)
            self.range_extra_frame.grid_propagate(False)

            self.rangeheader = tkinter.Label(self.range_frame, text="Range", font=self.font,
                                             fg=self.cfg.fg_color_header)
            self.rangeheader.place(relx=0.5, rely=0.165, anchor='center')
            self.rangelabel = tkinter.Label(self.range_current_frame, textvariable=self.rangevar, font=self.font,
                                            fg=self.cfg.fg_color_values)

            self.rangelabel.place(relx=0.5, rely=0.5, anchor='center')
            self.rangeextralabel = tkinter.Label(self.range_extra_frame, textvariable=self.rangeextravar,
                                                 font=self.font,
                                                 fg=self.cfg.fg_color_special)
            self.rangeextralabel.place(relx=0.5, rely=0.5, anchor='center')

        if self.cfg.refuel_activated:
            self.refuel_frame = ttk.Frame(self.overlay_frame, width=self.block_width, height=self.block_height)
            self.refuel_frame.grid(row=0, column=5)
            self.refuel_frame.grid_propagate(False)

            self.refuelheader = tkinter.Label(self.refuel_frame, text="Refuel", font=self.font,
                                              fg=self.cfg.fg_color_header)
            self.refuelheader.place(relx=0.5, rely=0.165, anchor='center')

            self.refuellabel = tkinter.Label(self.refuel_frame, textvariable=self.refuelvar, font=self.font,
                                             fg=self.cfg.fg_color_values)
            self.refuellabel.place(relx=0.5, rely=0.66, anchor='center')
