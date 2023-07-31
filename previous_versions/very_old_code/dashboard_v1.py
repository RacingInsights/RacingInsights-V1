from tkinter import Tk, Label, StringVar, Frame
from src.frontend.settings_vars import *


class SettingsWindow(Tk):
    def __init__(self):
        super().__init__()
        self.config(bg="#2B3A55")
        self.width = 600
        self.height = 800
        self.open_in_middle()

        # Add something that sets FONT_SIZE
        # Add something that sets TEXT_PADDING
        # Add something that sets offset_right_val, offset_down_val

    def open_in_middle(self):
        # get screen width and height
        ws = self.winfo_screenwidth()  # width of the screen
        hs = self.winfo_screenheight()  # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws / 2) - (self.width / 2)
        y = (hs / 2) - (self.height / 2)

        # set the dimensions of the screen
        # and where it is placed
        self.geometry('%dx%d+%d+%d' % (self.width, self.height, x, y))


class FuelTelemetryOverlay(Tk):
    def __init__(self):
        super().__init__()
        self.config(bg="PINK")
        # ------------------------------------ Column Frames -----------------------------------------------------------
        # Create separate frames for each parts of the dash
        self.fuel_frame = Frame(self, bg=color_dark_bg, width=block_width, height=block_height)
        self.fuel_frame.grid(row=0, column=0)
        # grid_propagate(False) to make sure it doesn't automatically resize to whatever is put inside!
        self.fuel_frame.grid_propagate(False)

        self.last_frame = Frame(self, bg=color_dark_bg, width=block_width, height=block_height)
        self.last_frame.grid(row=0, column=1)
        self.last_frame.grid_propagate(False)

        self.avg_frame = Frame(self, bg=color_dark_bg, width=block_width, height=block_height)
        self.avg_frame.grid(row=0, column=2)
        self.avg_frame.grid_propagate(False)

        self.target_frame = Frame(self, bg=color_dark_bg, width=block_width, height=block_height)
        self.target_frame.grid(row=0, column=3)
        self.target_frame.grid_propagate(False)

        self.laps_frame = Frame(self, bg=color_dark_bg, width=block_width, height=block_height)
        self.laps_frame.grid(row=0, column=4)
        self.laps_frame.grid_propagate(False)

        # Laps frame is divided in 3 sub-frames (2 values + 1 header)
        self.laps_current_frame = Frame(self.laps_frame, bg=color_dark_bg, width=block_width, height=target_sub_height)
        self.laps_current_frame.grid(row=1, column=0)
        self.laps_current_frame.grid_propagate(False)

        self.laps_extra_frame = Frame(self.laps_frame, bg=color_navy_bg, width=block_width, height=target_sub_height)
        self.laps_extra_frame.grid(row=2, column=0)
        self.laps_extra_frame.grid_propagate(False)

        # Target frame is divided in 3 sub-frames (2 values + 1 header)
        self.target_current_frame = Frame(self.target_frame, bg=color_dark_bg, width=block_width,
                                          height=target_sub_height)
        self.target_current_frame.grid(row=1, column=0)
        self.target_current_frame.grid_propagate(False)

        self.target_extra_frame = Frame(self.target_frame, bg=color_navy_bg, width=block_width,
                                        height=target_sub_height)
        self.target_extra_frame.grid(row=2, column=0)
        self.target_extra_frame.grid_propagate(False)

        # ------------------------------------ Header Frames -----------------------------------------------------------
        self.fuel_header_frame = Frame(self.fuel_frame, bg=color_dark_bg, width=block_width, height=target_sub_height)
        self.fuel_header_frame.grid(row=0, column=0)
        self.fuel_header_frame.grid_propagate(False)

        self.last_header_frame = Frame(self.last_frame, bg=color_dark_bg, width=block_width, height=target_sub_height)
        self.last_header_frame.grid(row=0, column=0)
        self.last_header_frame.grid_propagate(False)

        self.consumption_header_frame = Frame(self.avg_frame, bg=color_dark_bg, width=block_width,
                                              height=target_sub_height)
        self.consumption_header_frame.grid(row=0, column=0)
        self.consumption_header_frame.grid_propagate(False)

        self.target_header_frame = Frame(self.target_frame, bg=color_dark_bg, width=block_width,
                                         height=target_sub_height)
        self.target_header_frame.grid(row=0, column=0)
        self.target_header_frame.grid_propagate(False)

        self.laps_header_frame = Frame(self.laps_frame, bg=color_dark_bg, width=block_width, height=target_sub_height)
        self.laps_header_frame.grid(row=0, column=0)
        self.laps_header_frame.grid_propagate(False)

        # ------------------------------------ Header Labels -----------------------------------------------------------
        self.fuelheader = Label(self.fuel_frame, text="Fuel", font=FONT, fg=fg_color, bg=color_dark_bg)
        # Use .place() instead of grid or pack to set the position of the textlabels more precisely
        self.fuelheader.place(relx=0.5, rely=0.165, anchor='center')

        self.lastheader = Label(self.last_frame, text="Last", font=FONT, fg=fg_color, bg=color_dark_bg)
        self.lastheader.place(relx=0.5, rely=0.165, anchor='center')

        self.avgheader = Label(self.avg_frame, text="Avg", font=FONT, fg=fg_color, bg=color_dark_bg)
        self.avgheader.place(relx=0.5, rely=0.165, anchor='center')

        self.targetheader = Label(self.target_frame, text="Target", font=FONT, fg=fg_color, bg=color_dark_bg)
        self.targetheader.place(relx=0.5, rely=0.165, anchor='center')

        self.lapsheader = Label(self.laps_frame, text="Laps", font=FONT, fg=fg_color, bg=color_dark_bg)
        self.lapsheader.place(relx=0.5, rely=0.165, anchor='center')

        # ------------------------------------ Value Labels ------------------------------------------------------------
        self.fuelvar = StringVar()
        self.fuelvar.set("000.00")
        self.fuellabel = Label(self.fuel_frame, textvariable=self.fuelvar, font=FONT, bg=color_dark_bg,
                               fg=fg_color_vals)
        self.fuellabel.place(relx=0.5, rely=0.66, anchor='center')

        self.lastvar = StringVar()
        self.lastvar.set("000.00")
        self.lastlabel = Label(self.last_frame, textvariable=self.lastvar, font=FONT, bg=color_dark_bg,
                               fg=fg_color_vals)
        self.lastlabel.place(relx=0.5, rely=0.66, anchor='center')

        self.avgvar = StringVar()
        self.avgvar.set("000.00")
        self.avglabel = Label(self.avg_frame, textvariable=self.avgvar, font=FONT, bg=color_dark_bg, fg=fg_color_vals)
        self.avglabel.place(relx=0.5, rely=0.66, anchor='center')

        self.targetcurrentvar = StringVar()
        self.targetcurrentvar.set("000.00")
        self.targetcurrentlabel = Label(self.target_current_frame, textvariable=self.targetcurrentvar, font=FONT,
                                        bg=color_dark_bg, fg=fg_color_vals)
        self.targetcurrentlabel.place(relx=0.5, rely=0.5, anchor='center')

        self.targetextravar = StringVar()
        self.targetextravar.set("000.00")
        self.targetextralabel = Label(self.target_extra_frame, textvariable=self.targetextravar, font=FONT,
                                      bg=color_navy_bg, fg=fg_color_extra_vals)
        self.targetextralabel.place(relx=0.5, rely=0.5, anchor='center')

        self.lapsvar = StringVar()
        self.lapsvar.set("000.00")
        self.lapslabel = Label(self.laps_current_frame, textvariable=self.lapsvar, font=FONT, bg=color_dark_bg,
                               fg=fg_color_vals)
        self.lapslabel.place(relx=0.5, rely=0.5, anchor='center')

        self.lapsextravar = StringVar()
        self.lapsextravar.set("000.00")
        self.lapsextralabel = Label(self.laps_extra_frame, textvariable=self.lapsextravar, font=FONT, bg=color_navy_bg,
                                    fg=fg_color_extra_vals)
        self.lapsextralabel.place(relx=0.5, rely=0.5, anchor='center')

        # ------------------------------------ Global appearance -------------------------------------------------------
        # Set how much space the dashboard window can cover
        # self.geometry(f"{5 * block_width}x{int(block_height)}")

        # # Make everything transparent
        # self.attributes('-alpha', 0.9)

        #  Make only the elements with PINK color transparent
        self.wm_attributes('-transparentcolor', 'PINK')

        # Make it not clickable and remove the bar on top with min, max, close buttons
        self.overrideredirect(True)

        # Move it away from the border using .geometry("+5+5") -> 5 right, 5 down
        self.geometry(f"+{OFFSET_RIGHT}+{OFFSET_DOWN}")

        # Lift the dashboard above others (not sure if lift is necessary when attribute is set to topmost?)
        self.lift()
        self.wm_attributes("-topmost", True)
