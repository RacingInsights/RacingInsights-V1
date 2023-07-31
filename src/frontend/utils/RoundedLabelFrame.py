import tkinter
from math import cos, sin
from typing import Optional

class RoundedLabelFrame:
    """
    Acts like a tkinter frame but can show as a rounded frame with
    smooth corners.

    It can receive telemetry, just set the self.text to the telemetry string
    and the frame will update it automatically (using a property)

    Changing the appearance can be done by changing the
    attributes listed under # Configurable settings.
    Whenever an appearance change is made from outside, the .configure()
    method should be called.

    NOTE: Uses a lower limit that it will always use for the size,
    this can be influenced by changing the value for self.min_txt_length
    Hence, setting the width or height doesn't always influence the size
    as these might be constrained to the text that is inside.
    """
    feather_ratio = 15
    my_label_padding_x = 0
    my_label_padding_y = 0

    def __init__(self, master: tkinter.Tk | tkinter.Toplevel | tkinter.Frame,
                 textvariable: tkinter.StringVar,
                 side=None,
                 bg: str = "GREEN",
                 width: int = 0,
                 height: int = 0,
                 fill: str = "ORANGE",
                 font_size: int = 16,
                 font_color: str = "BLACK",
                 padx: int = 0,
                 pady: int = 0,
                 txt_len: Optional[int] = 6
                 ):

        # Configurable settings:
        self.bg = bg
        self.set_width = width
        self.set_height = height
        self.fill = fill
        self.font_size = font_size
        self.font_color = font_color
        self.padx = padx
        self.pady = pady
        self.min_txt_length = txt_len
        self.side = side

        # Settable for data
        self.string_var = textvariable

        # Fixed settings
        self._font_style = "TkFixedFont"
        self._font_extra = "bold"
        self._label_check = tkinter.Label(font=self.font, text=self.min_text_ref, padx=0, pady=0)

        # Initialize the UI - Uses a master same as a tkinter frame would
        self.master = master

        # The "frame" is the container, hence it replaces a normal tkinter frame and adds functionality
        self.frame = tkinter.Frame(master=self.master, bg=self.bg)

        self.canvas = tkinter.Canvas(master=self.frame,
                                     bg=self.bg,
                                     width=self.set_width,
                                     height=self.set_height,
                                     borderwidth=0,
                                     highlightthickness=0,
                                     )

        points = self._get_rectangle_points(x1=0, y1=0,
                                            width=self.set_width,
                                            height=self.set_height,
                                            feather=int(self.set_width / self.feather_ratio))

        self.rounded_rectangle = self._draw_rounded_rectangle(points=points, fill=self.fill)

        self.label = tkinter.Label(master=self.frame, textvariable=self.string_var, fg=self.font_color, bg=self.fill,
                                   padx=0, pady=0)
        self.label.pack(fill=tkinter.BOTH, expand=True)
        self.label_window = self.canvas.create_window(int(self.width / 2),
                                                      int(self.height / 2),
                                                      window=self.label)

    def pack(self, side):
        self.side = side
        self.frame.pack(side=self.side, padx=self.padx, pady=self.pady, fill=tkinter.BOTH, expand=True)
        self.canvas.pack(fill=tkinter.BOTH, expand=True)

    def pack_forget(self):
        for widget in self.frame.winfo_children():
            widget.pack_forget()
        self.frame.pack_forget()

    def change_rounded_rectangle_color(self):
        """
        Specializes in changing the color inside the rounded rectangle as this might often be
        associated with telemetry. Allows to avoid running the lengthy .configure() when not needed.

        Note, this should only be called after changing the self.fill attribute!
        """
        self.label.configure(bg=self.fill)
        self.canvas.itemconfigure(self.rounded_rectangle, fill=self.fill)

    def configure(self):
        """re-configures the appearance elements. To be called when changed attributes from outside."""
        self.frame.configure(padx=self.padx, pady=self.pady)
        self.label.configure(font=self.font, bg=self.fill, fg=self.font_color)
        self.canvas.configure(width=self.width, height=self.height, bg=self.bg)
        self.reconfigure_rounded_rectangle()
        self.canvas.coords(self.label_window, int(self.width / 2), int(self.height / 2))

    def _draw_rounded_rectangle(self, points, **kwargs):
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    @property
    def min_text_ref(self) -> str:
        min_text = ""
        for i in range(self.min_txt_length):
            min_text += "1"
        return min_text

    @property
    def font(self):
        return f"{self._font_style} " \
               f"{self.font_size} " \
               f"{self._font_extra}"

    @property
    def height(self) -> int:
        self._label_check.config(font=self.font)
        return max(self._label_check.winfo_reqheight() + self.my_label_padding_y, self.set_height)

    @property
    def width(self) -> int:
        self._label_check.config(font=self.font)
        return max(self._label_check.winfo_reqwidth() + self.my_label_padding_x, self.set_width)

    @property
    def my_feather(self) -> int:
        return int(self.width / self.feather_ratio)

    def reconfigure_rounded_rectangle(self):
        """
        This combined with the properties provides the magic sauce for having rounded corners
        and have them updatable/reconfigurable
        """
        points = self._get_rectangle_points(x1=0, y1=0, width=self.width, height=self.height,
                                            feather=self.my_feather)
        self.canvas.coords(self.rounded_rectangle, points)
        self.canvas.itemconfigure(self.rounded_rectangle, fill=self.fill)

    @staticmethod
    def _get_rectangle_points(x1, y1, width, height, feather, res=10):
        x2, y2 = x1 + width, y1 + height
        points = []
        # top side
        points += [x1 + feather, y1,
                   x2 - feather, y1]
        # top right corner
        for i in range(res):
            points += [x2 - feather + sin(i / res * 2) * feather,
                       y1 + feather - cos(i / res * 2) * feather]
        # right side
        points += [x2, y1 + feather,
                   x2, y2 - feather]
        # bottom right corner
        for i in range(res):
            points += [x2 - feather + cos(i / res * 2) * feather,
                       y2 - feather + sin(i / res * 2) * feather]
        # bottom side
        points += [x2 - feather, y2,
                   x1 + feather, y2]
        # bottom left corner
        for i in range(res):
            points += [x1 + feather - sin(i / res * 2) * feather,
                       y2 - feather + cos(i / res * 2) * feather]
        # left side
        points += [x1, y2 - feather,
                   x1, y1 + feather]
        # top left corner
        for i in range(res):
            points += [x1 + feather - cos(i / res * 2) * feather,
                       y1 + feather - sin(i / res * 2) * feather]
        return points

# # Example use:
# root = tkinter.Tk()
# root.overrideredirect(True)
# root.geometry(f"+{100}+{100}")
#
# initial_size = 100
#
# main_frame = tkinter.Frame(master=root, bg="PURPLE")
# main_frame.pack(fill=tkinter.BOTH, expand=True)
#
# my_frame = RoundedLabelFrame(master=main_frame, width=initial_size, height=initial_size, fill="ORANGE", text="Hello",
#                         padx=10, side='right')
# my_frame2 = RoundedLabelFrame(master=main_frame, width=initial_size, height=initial_size, fill="BLUE",
#                          text="RI",
#                          font_color="RED")
#
# screen2 = tkinter.Toplevel()
# screen2.overrideredirect(True)
# screen2.geometry(f"+{500}+{700}")
#
#
# def update_width(_):
#     print("----------------")
#     new_width = int(slider.get())
#     my_frame.set_width = new_width
#     my_frame2.set_width = new_width
#     my_frame.set_height = new_width
#     my_frame2.set_height = new_width
#
#
# slider = tkinter.Scale(master=screen2,
#                        from_=0, to=500,
#                        orient='horizontal',
#                        length=200,
#                        )
#
# slider.set(my_frame.width)
# slider.pack()
# slider.bind("<ButtonRelease-1>", update_width)
#
#
# def update_fontsize(_):
#     dont_size = int(slider2.get())
#     my_frame.font_size = dont_size
#     my_frame2.font_size = dont_size
#
#
# slider2 = tkinter.Scale(master=screen2,
#                         from_=1, to=100,
#                         orient='horizontal',
#                         length=200,
#                         )
# slider2.set(my_frame.font_size)
# slider2.pack()
# slider2.bind("<ButtonRelease-1>", update_fontsize)
#
# while True:
#     root.update()
#     my_frame.configure()
#     my_frame2.configure()
