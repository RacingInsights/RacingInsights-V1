import tkinter

from previous_versions.Version_Before_Refactor.src.frontend.configurations import FuelScreenConfig, RelativeScreenConfig
from previous_versions.Version_Before_Refactor.src.frontend.overlays.utils.rounded_rectangle import create_good_rectangle


class OverlayAbstract:
    def __init__(self, parent_obj, rounded: bool, overlay_type: str, config_data):
        """
        overlay_type: options: "fuel", "relative, "..." new overlays to be added
        config_data: Configuration data used for setting/storing the appearance settings
        locked: Boolean indicating whether this overlay can be dragged (locked = False) or not (locked = True)
        rounded: Boolean indicating whether this overlay has rounded corners or not

        parent_obj: This refers to the MainScreen object. This object connects to all overlays.
        (Mostly used as pointer to obj)
        master: Toplevel object that acts as the container to hold all the tkinter widgets inside
        overlay_canvas: Canvas object needed for combining the overlay_frame (square) and the rounded rectangle
        (overlay box)
        overlay_frame: square Frame object that acts as the container for the overlay specific widgets
        """
        self.rectangle = None
        self.y = None
        self.x = None

        self.parent_obj = parent_obj  # This should be storing the MainScreen instance
        self.rounded: bool = rounded
        self.overlay_type: str = overlay_type
        self.config_data = config_data

        self.locked = True

        self.cfg = self.load_cfg()

        self.master = tkinter.Toplevel(self.parent_obj.master)

        self.set_master_settings()

        self.overlay_canvas = tkinter.Canvas(master=self.master, borderwidth=0, highlightthickness=0, bg="RED",
                                             width=1920, height=1080)
        self.overlay_frame = tkinter.Frame(master=self.overlay_canvas, bg=self.cfg.bg_color)

        self.overlay_canvas.pack(expand=1, fill='both')
        self.overlay_frame.pack()

        if self.rounded:
            # Create a temporary window, just to spawn the widgets before calculating/spawning the final window
            self.overlay_canvas.create_window(0, 0, window=self.overlay_frame)

    def set_master_settings(self):
        """
        Sets all necessary settings for the master
        :return:
        """
        self.master.title("")
        self.master.withdraw()
        self.master.geometry(f"+{self.cfg.offset_right}+{self.cfg.offset_down}")
        self.master.overrideredirect(True)
        self.master.lift()
        self.master.wm_attributes("-topmost", True)
        self.master.attributes('-alpha', 0.95)
        self.master.wm_attributes('-transparentcolor', "RED")
        self.master.iconbitmap("images/RacingInsights_Logo.ico")

    def load_cfg(self):
        cfg = None
        match self.overlay_type:
            case "fuel":
                cfg = FuelScreenConfig(**self.config_data['fuel'])
            case "relative":
                cfg = RelativeScreenConfig(**self.config_data['relative'])
        return cfg

    def make_overlay_rounded(self):
        """
        Calculate the size of the (square) overlay_frame and makes the overlay appear rounded with some padding
        :return:
        """
        # After putting all the content inside the frame, measure its size
        self.overlay_frame.update()  # Needs to be updated before measurements
        frame_width = self.overlay_frame.winfo_width()
        frame_height = self.overlay_frame.winfo_height()

        # Create the rounded rectangle based on inner frame dimensions
        window_padding = 15
        window_width = frame_width + window_padding
        window_height = frame_height + window_padding

        if self.rectangle:
            self.overlay_canvas.delete(self.rectangle)

        self.rectangle = create_good_rectangle(self.overlay_canvas, 0, 0, window_width, window_height, feather=10,
                                               color=self.cfg.bg_color)

        self.overlay_canvas.create_window(window_width / 2, window_height / 2, window=self.overlay_frame)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, _):
        self.x = None
        self.y = None

    def do_move(self, event):
        delta_x = event.x - self.x
        delta_y = event.y - self.y
        self.cfg.offset_right = self.master.winfo_x() + delta_x
        self.cfg.offset_down = self.master.winfo_y() + delta_y
        self.master.geometry(f"+{self.cfg.offset_right}+{self.cfg.offset_down}")

    def set_drag_bind(self, bl_bind_on: bool):
        if bl_bind_on:
            self.master.bind("<ButtonPress-1>", self.start_move)
            self.master.bind("<ButtonRelease-1>", self.stop_move)
            self.master.bind("<B1-Motion>", self.do_move)
        else:
            self.master.unbind("<ButtonPress-1>")
            self.master.unbind("<ButtonRelease-1>")
            self.master.unbind("<B1-Motion>")

    def update_cfg_value(self, setting, value):
        if hasattr(self, 'cfg'):
            cfg_attr = getattr(self, 'cfg')
            if hasattr(cfg_attr, setting):
                setattr(cfg_attr, setting, value)
