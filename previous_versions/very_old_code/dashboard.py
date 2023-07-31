import threading
import time
from tkinter import Tk, Label, StringVar, Frame, Button, Toplevel, Scale, messagebox
import logging
# from functools import partial # allows for passing both a function as well as its arguments, in case of "command=partial(func, arg1, arg2)"

from previous_versions.very_old_code.load_config import load_config, save_in_config
from src.frontend.hover_info import HoverInfoWindow

class ChildScreen:
    def __init__(self, parent_obj, width=None, height=None):
        self.parent_obj = parent_obj
        self.master = Toplevel(self.parent_obj.master)

        self.width = width
        self.height = height

        self.set_window_size()

        # Load the configuration file
        load_config(self)

    def set_window_size(self):
        """
        Changes the geometry of the master window in case desired dimensions are given
        (if not given, the window's size will automatically adjust to contents inside)
        """
        if self.width and self.height:
            self.master.geometry('%dx%d' % (self.width, self.height))

    def open_in_middle(self):
        """
        Opens the window in the middle of the screen
        :return:
        """
        # get screen width and height
        ws = self.master.winfo_screenwidth()  # width of the screen
        hs = self.master.winfo_screenheight()  # height of the screen

        # calculate x and y coordinates for the Toplevel master window
        x = (ws / 2) - (self.width / 2)
        y = (hs / 2) - (self.height / 2)

        # Add offsets to center the window
        self.master.geometry('+%d+%d' % (x, y))

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.master.winfo_x() + deltax
        y = self.master.winfo_y() + deltay
        self.master.geometry(f"+{x}+{y}")
    def set_drag_bind(self, bl_bind_on):
        if bl_bind_on:
            self.master.bind("<ButtonPress-1>", self.start_move)
            self.master.bind("<ButtonRelease-1>", self.stop_move)
            self.master.bind("<B1-Motion>", self.do_move)
        else:
            self.master.unbind("<ButtonPress-1>")
            self.master.unbind("<ButtonRelease-1>")
            self.master.unbind("<B1-Motion>")


class MainScreen:
    def __init__(self, master: Tk, telemetry, ir_conn, state, width, height):
        # Load the configuration file
        load_config(self)

        # Initialization
        self.master = master
        self.master.iconbitmap("docs/RacingInsights_Logo.ico")
        self.master.title("RacingInsights")
        self.master.config(width=width, height=height, bg=self.bg_color)

        self.width = width
        self.height = height

        self.open_in_middle()

        self.fuel_open = False
        self.settings_open = False

        self.telemetry = telemetry
        self.ir_conn = ir_conn
        self.state = state

        self.font = f'{self.font_style} {self.font_size} {self.font_extra}'

        self.button1 = Button(self.master, text='Open Fuel Overlay', font=self.font, width=self.button_width, fg=self.fg_color, height=self.button_height, command=self.open_fuel, bg=self.button_color)
        self.button1.place(relx=0.5, rely=(1/3),anchor='center')

        self.button_settings = Button(self.master, text='Settings', font=self.font, width=self.button_width, height=self.button_height, fg=self.fg_color, bg=self.button_color, command=self.open_settings)
        self.button_settings.place(relx=0.5, rely=(2/3), anchor='center')

    def open_in_middle(self):
        # get screen width and height
        ws = self.master.winfo_screenwidth()  # width of the screen
        hs = self.master.winfo_screenheight()  # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws / 2) - (self.width / 2)
        y = (hs / 2) - (self.height / 2)

        # set the dimensions of the screen and where it is placed
        self.master.geometry('%dx%d+%d+%d' % (self.width, self.height, x, y))

    def open_fuel(self):
        """
        Creates and opens the fuel window and a separate thread for updating its values periodically
        :return:
        """
        if self.fuel_open == False:
            self.fuel_app = FuelScreen(parent_obj=self, width=None, height=None, telemetry=self.telemetry, ir_conn=self.ir_conn, state=self.state)
            self.fuel_open = True

    def open_settings(self):
        """
        Opens the settings window. This settings window can be used to change the appearance of the overlays.
        :return:
        """
        if self.settings_open == False:
            self.settings_open = True
            self.settings_app = SettingsScreen(parent_obj=self, width=1200, height= 600)


class SettingsScreen(ChildScreen):
    def __init__(self,parent_obj, width, height):
        super().__init__(parent_obj, width, height)
        # Initialization
        self.master.config(bg=self.bg_color)
        self.master.title("Settings")

        self.open_in_middle()

        self.master.lift()

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Make sure to open the fuel app before opening the UI elements in SettingsScreen linked to the fuel app
        self.parent_obj.open_close_fuel()

        self.font = f'{self.font_style} {self.font_size} {self.font_extra}'

        self.init_visuals()

    def on_closing(self):
        if messagebox.askyesno(title="Unsaved settings",message= "Would you like to save these current settings?"):
            logging.info("The user asked to save the settings in the config file")
            self.save_settings_in_config()
        else:
            logging.info("The user asked not to save the settings, current config is reloaded")
            load_config(self.parent_obj.fuel_app)
            self.parent_obj.fuel_app.master.geometry(f"+{self.parent_obj.fuel_app.offset_right}+{self.parent_obj.fuel_app.offset_down}")
            self.parent_obj.fuel_app.update_visuals()
        self.lock_fuel_lock()

        logging.info("Settings window closed")
        # Set the settings_open boolean of the parent_obj to False to allow for re-opening the settings window again
        self.parent_obj.settings_open = False
        self.master.destroy()

    def save_settings_in_config(self):
        fuelscreen_font_size = self.fontsize_slider.get()
        fuelscreen_text_padding = self.textpadding_slider.get()
        fuelscreen_offset_right = self.parent_obj.fuel_app.master.winfo_x()
        fuelscreen_offset_down = self.parent_obj.fuel_app.master.winfo_y()

        save_in_config( font_size=["FUELSCREEN",fuelscreen_font_size],
                        text_padding=["FUELSCREEN",fuelscreen_text_padding],
                        offset_right=["FUELSCREEN",fuelscreen_offset_right],
                        offset_down=["FUELSCREEN",fuelscreen_offset_down])

    def init_visuals(self):
        """
        Initializes the visual elements of the settings window
        :return:
        """
        settings_block_width = 200
        settings_block_height = 100

        self.fontsize_frame = Frame(self.master, bg=self.bg_color, width=settings_block_width, height=settings_block_height)
        self.fontsize_frame.pack(pady=10)
        self.textpadding_frame = Frame(self.master, bg=self.bg_color, width=settings_block_width, height=settings_block_height)
        self.textpadding_frame.pack(pady=10)

        self.lockbutton_frame = Frame(self.master, bg="RED", width=settings_block_width, height=settings_block_height)
        self.lockbutton_frame.pack(pady=10)

        self.fontsize_label = Label(self.fontsize_frame, text="Font size", font=self.parent_obj.font, bg=self.bg_color, fg=self.fg_color)
        self.fontsize_label.pack(fill='both')
        self.fontsize_slider = Scale(self.fontsize_frame, from_=7, to=30, orient='horizontal', command=self.set_font_size)
        self.fontsize_slider.set(self.parent_obj.fuel_app.font_size)
        self.fontsize_slider.pack()

        self.textpadding_label = Label(self.textpadding_frame, text="Text padding", font=self.parent_obj.font, bg=self.bg_color, fg=self.fg_color)
        self.textpadding_label.pack(fill='both')
        self.textpadding_slider = Scale(self.textpadding_frame, from_=0, to=50, orient='horizontal', command=self.set_text_padding)
        self.textpadding_slider.set(self.parent_obj.fuel_app.text_padding)
        self.textpadding_slider.pack()

        self.lockbutton = Button(self.lockbutton_frame, text='Toggle Fuel Lock', font=self.font, width=self.button_width, height=self.button_height, fg=self.fg_color, bg=self.button_color, command=self.toggle_fuel_lock)
        self.lockbutton.pack()

        # Add a hover info window to explain the button's functionality
        self.lockbutton_hover_info = HoverInfoWindow(master_widget=self.lockbutton,text="lock or unlock the fuel overlay to position it to your liking")

    def lock_fuel_lock(self):
        if not (self.parent_obj.fuel_app.locked):
            self.parent_obj.fuel_app.set_drag_bind(False)
            self.parent_obj.fuel_app.locked = True

    def toggle_fuel_lock(self):
        self.parent_obj.fuel_app.locked = not(self.parent_obj.fuel_app.locked)

        if not (self.parent_obj.fuel_app.locked):
            self.parent_obj.fuel_app.set_drag_bind(True)
        else:
            self.parent_obj.fuel_app.set_drag_bind(False)

    def set_font_size(self, value):
        font_size = int(value)
        self.parent_obj.fuel_app.resize_text(font_size=font_size)

    def set_text_padding(self, value):
        text_padding = int(value)
        self.parent_obj.fuel_app.resize_padding(text_padding=text_padding)


class FuelScreen(ChildScreen):
    def __init__(self, parent_obj, width, height, telemetry, ir_conn, state):
        super().__init__(parent_obj, width, height)
        # Initialization
        self.master.title("FuelScreen")
        self.master.geometry(f"+{self.offset_right}+{self.offset_down}")
        self.master.overrideredirect(True)
        self.master.lift()
        self.master.wm_attributes("-topmost", True)

        self.set_styling_vars()

        self.locked = True

        self.init_visuals()

        # Create a thread for updating the dashboard data
        thread = threading.Thread(target=self.update_dash, args=[telemetry, ir_conn, state])
        # Set this thread to be a daemon, this way the application will close when all non-daemon threads are closed
        # (the only non daemonic thread should be the main thread for this functionality)
        thread.daemon = True
        thread.start()

    def set_styling_vars(self):
        """
        sets the variables that are dependent on input (=settings) variables
        font, block width, block height, block sub height
        :return:
        """
        self.font = f'{self.font_style} {self.font_size} {self.font_extra}'

        # Automatically calculate the block dimensions with font size and text padding as customizable settings
        self.block_width, self.block_height = int(self.font_size * 4.5 + self.text_padding), int(self.font_size * 5 + self.text_padding)
        self.block_sub_height = int(self.block_height / 3)

        # Calculate the value of the lower sub block to prevent 1 pixel offset due to mod(block_height,3) NOT being a natural number (N)
        self.block_sub_height_last = self.block_height - 2*self.block_sub_height

    def update_dash(self, tm, ir_conn, state):
        """
        Loop that updates the frontend (dashboard) based on the data it gets from the backend (iRacing telemetry).
        Note that this function is supposed to be called in a different thread than the main
        :param tm:
        :param ir_conn:
        :param state:
        :return:
        """
        while True:
            # Update the telemetry data
            tm.step(state=state, ir_conn=ir_conn)

            # Update the frontend if still connected
            if state.ir_connected:
                self.fuelvar.set(f"{tm.fuel:.2f}")
                self.lastvar.set(f"{tm.cons:.2f}")
                self.avgvar.set(f"{tm.avg_cons:.2f}")
                self.targetcurrentvar.set(f"{tm.target_cons_current:.2f}")
                self.targetextravar.set(f"{tm.target_cons_extra:.2f}")
                self.lapsvar.set(f"{tm.laps_left_current}")
                self.lapsextravar.set(f"{tm.laps_left_extra}")

            # Go to sleep. Minimum step-time is (1/60) seconds (=approx 17ms) as iRacing telemetry is updated at 60 Hz.
            step_time = 1
            time.sleep(step_time)



    def respawn_visuals(self):
        self.set_styling_vars()
        self.clear_frame(self.fuel_frame)
        self.clear_frame(self.last_frame)
        self.clear_frame(self.avg_frame)
        self.clear_frame(self.target_frame)
        self.clear_frame(self.laps_frame)
        self.init_visuals()
    def resize_text(self,font_size):
        self.font_size = font_size
        self.respawn_visuals()
    def resize_padding(self, text_padding):
        self.text_padding = text_padding
        self.respawn_visuals()
    def change_offset_right(self, offset_right):
        self.offset_right = offset_right
        self.master.geometry(f"+{self.offset_right}+{self.offset_down}")
    def change_offset_down(self, offset_down):
        self.offset_down = offset_down
        self.master.geometry(f"+{self.offset_right}+{self.offset_down}")
    def clear_frame(self, frame):
        frame.grid_forget()
        for widgets in frame.winfo_children():
            widgets.destroy()

    def init_visuals(self):
        """
        Adds the visual elements of the fuel overlay
        :return:
        """
        # ------------------------------------ FUEL ------------------------------------------------------------
        self.fuel_frame = Frame(self.master, bg=self.bg_color, width=self.block_width, height=self.block_height)
        self.fuel_frame.grid(row=0, column=0)
        self.fuel_frame.grid_propagate(False)
        # ------------------------------------ Header Labels -----------------------------------------------------------
        self.fuelheader = Label(self.fuel_frame, text="Fuel", font=self.font, fg=self.color_header, bg=self.bg_color)
        # Use .place() instead of grid or pack to set the position of the textlabels more precisely
        self.fuelheader.place(relx=0.5, rely=0.165, anchor='center')
        # ------------------------------------ Value Labels ------------------------------------------------------------
        self.fuelvar = StringVar(master=self.fuel_frame)
        self.fuelvar.set("000.00")
        self.fuellabel = Label(self.fuel_frame, textvariable=self.fuelvar, font=self.font, bg=self.bg_color, fg=self.color_values)
        self.fuellabel.place(relx=0.5, rely=0.66, anchor='center')

        # ------------------------------------ LAST ------------------------------------------------------------
        self.last_frame = Frame(self.master, bg=self.bg_color, width=self.block_width, height=self.block_height)
        self.last_frame.grid(row=0, column=1)
        self.last_frame.grid_propagate(False)

        self.lastheader = Label(self.last_frame, text="Last", font=self.font, fg=self.color_header, bg=self.bg_color)
        self.lastheader.place(relx=0.5, rely=0.165, anchor='center')

        self.lastvar = StringVar()
        self.lastvar.set("000.00")
        self.lastlabel = Label(self.last_frame, textvariable=self.lastvar, font=self.font, bg=self.bg_color, fg=self.color_values)
        self.lastlabel.place(relx=0.5, rely=0.66, anchor='center')

        # ------------------------------------ AVG ------------------------------------------------------------
        self.avg_frame = Frame(self.master, bg=self.bg_color, width=self.block_width, height=self.block_height)
        self.avg_frame.grid(row=0, column=2)
        self.avg_frame.grid_propagate(False)

        self.avgheader = Label(self.avg_frame, text="Avg", font=self.font, fg=self.color_header, bg=self.bg_color)
        self.avgheader.place(relx=0.5, rely=0.165, anchor='center')

        self.avgvar = StringVar()
        self.avgvar.set("000.00")
        self.avglabel = Label(self.avg_frame, textvariable=self.avgvar, font=self.font, bg=self.bg_color, fg=self.color_values)
        self.avglabel.place(relx=0.5, rely=0.66, anchor='center')

        # ------------------------------------ TARGET ------------------------------------------------------------
        self.target_frame = Frame(self.master, bg=self.bg_color, width=self.block_width, height=self.block_height)
        self.target_frame.grid(row=0, column=3)
        self.target_frame.grid_propagate(False)

        # Target frame is divided in 3 sub-frames (2 values + 1 header)
        self.target_header_frame = Frame(self.target_frame, bg=self.bg_color, width=self.block_width, height=self.block_sub_height)
        self.target_header_frame.grid(row=0, column=0)
        self.target_header_frame.grid_propagate(False)

        self.target_current_frame = Frame(self.target_frame, bg=self.bg_color, width=self.block_width, height=self.block_sub_height)
        self.target_current_frame.grid(row=1, column=0)
        self.target_current_frame.grid_propagate(False)

        self.target_extra_frame = Frame(self.target_frame, bg=self.bg_color_special, width=self.block_width, height=self.block_sub_height_last)
        self.target_extra_frame.grid(row=2, column=0)
        self.target_extra_frame.grid_propagate(False)

        self.targetheader = Label(self.target_frame, text="Target", font=self.font, fg=self.color_header, bg=self.bg_color)
        self.targetheader.place(relx=0.5, rely=0.165, anchor='center')

        self.targetcurrentvar = StringVar()
        self.targetcurrentvar.set("000.00")
        self.targetcurrentlabel = Label(self.target_current_frame, textvariable=self.targetcurrentvar, font=self.font, bg=self.bg_color, fg=self.color_values)
        self.targetcurrentlabel.place(relx=0.5, rely=0.5, anchor='center')

        self.targetextravar = StringVar()
        self.targetextravar.set("000.00")
        self.targetextralabel = Label(self.target_extra_frame, textvariable=self.targetextravar, font=self.font, bg=self.bg_color_special, fg=self.color_special)
        self.targetextralabel.place(relx=0.5, rely=0.5, anchor='center')

        # ------------------------------------ LAPS ------------------------------------------------------------
        self.laps_frame = Frame(self.master, bg=self.bg_color, width=self.block_width, height=self.block_height)
        self.laps_frame.grid(row=0, column=4)
        self.laps_frame.grid_propagate(False)

        # Laps frame is divided in 3 sub-frames (2 values + 1 header)
        self.laps_header_frame = Frame(self.laps_frame, bg=self.bg_color, width=self.block_width, height=self.block_sub_height)
        self.laps_header_frame.grid(row=0, column=0)
        self.laps_header_frame.grid_propagate(False)

        self.laps_current_frame = Frame(self.laps_frame, bg=self.bg_color, width=self.block_width, height=self.block_sub_height)
        self.laps_current_frame.grid(row=1, column=0)
        self.laps_current_frame.grid_propagate(False)

        self.laps_extra_frame = Frame(self.laps_frame, bg=self.bg_color_special, width=self.block_width, height=self.block_sub_height_last)
        self.laps_extra_frame.grid(row=2, column=0, sticky='SE', pady=0)
        self.laps_extra_frame.grid_propagate(False)

        self.lapsheader = Label(self.laps_frame, text="Laps", font=self.font, fg=self.color_header, bg=self.bg_color)
        self.lapsheader.place(relx=0.5, rely=0.165, anchor='center')

        self.lapsvar = StringVar()
        self.lapsvar.set("000.00")
        self.lapslabel = Label(self.laps_current_frame, textvariable=self.lapsvar, font=self.font, bg=self.bg_color, fg=self.color_values)
        self.lapslabel.place(relx=0.5, rely=0.5, anchor='center')

        self.lapsextravar = StringVar()
        self.lapsextravar.set("000.00")
        self.lapsextralabel = Label(self.laps_extra_frame, textvariable=self.lapsextravar, font=self.font, bg=self.bg_color_special, fg=self.color_special)
        self.lapsextralabel.place(relx=0.5, rely=0.5, anchor='center')
