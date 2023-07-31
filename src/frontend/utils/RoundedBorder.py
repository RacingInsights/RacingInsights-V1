import tkinter
from math import cos, sin


def get_rectangle_points(x1, y1, width, height, feather, res=10):
    x2, y2 = x1 + width, y1 + height
    _points = []
    # top side
    _points += [x1 + feather, y1,
                x2 - feather, y1]
    # top right corner
    for i in range(res):
        _points += [x2 - feather + sin(i / res * 2) * feather,
                    y1 + feather - cos(i / res * 2) * feather]
    # right side
    _points += [x2, y1 + feather,
                x2, y2 - feather]
    # bottom right corner
    for i in range(res):
        _points += [x2 - feather + cos(i / res * 2) * feather,
                    y2 - feather + sin(i / res * 2) * feather]
    # bottom side
    _points += [x2 - feather, y2,
                x1 + feather, y2]
    # bottom left corner
    for i in range(res):
        _points += [x1 + feather - sin(i / res * 2) * feather,
                    y2 - feather + cos(i / res * 2) * feather]
    # left side
    _points += [x1, y2 - feather,
                x1, y1 + feather]
    # top left corner
    for i in range(res):
        _points += [x1 + feather - cos(i / res * 2) * feather,
                    y1 + feather - sin(i / res * 2) * feather]
    return _points


class RoundedBorder:
    my_feather = 5
    my_padding = 2*my_feather

    def __init__(self, master: tkinter.Toplevel, bg: str):
        self.master = master
        self.canvas = tkinter.Canvas(master=self.master, bg="RED", highlightthickness=0, borderwidth=0)
        self.canvas.pack()

        self.frame = tkinter.Frame(master=self.master, bg=bg, width=300,
                                   height=300)  # This contains all contents!!!

        center_x = self.canvas.winfo_reqwidth() // 2
        center_y = self.canvas.winfo_reqheight() // 2

        self.window = self.canvas.create_window(center_x, center_y, anchor="center",
                                                window=self.frame)  # just init, pos dont matter

        points = get_rectangle_points(x1=0, y1=0,
                                      width=self.canvas_width,
                                      height=self.canvas_height,
                                      feather=self.my_feather)

        self.rounded_border = self._draw_rounded_rectangle(points=points, fill=bg)

        # Every time the frame is resized, the border and window need to be resized too
        self.frame.bind("<Configure>", self.reconfigure_rounded_border)

        self.reconfigure_rounded_border(None)  # Call once to make sure it's correctly set at start

    def reconfigure_rounded_border(self, _):
        # Set new size for canvas
        new_canvas_width = self.frame.winfo_reqwidth() + self.my_padding
        if new_canvas_width % 2 != 0:
            new_canvas_width += 1
        new_canvas_height = self.frame.winfo_reqheight() + self.my_padding
        if new_canvas_height % 2 != 0:
            new_canvas_height += 1

        self.canvas.configure(width=new_canvas_width, height=new_canvas_height)

        # Relocate the window for the frame inside this resized canvas
        # The offset = 2 is there to remove the small offset created by the canvas
        offset = 0
        self.canvas.coords(self.window, new_canvas_width // 2 + offset, new_canvas_height // 2 + offset)

        # Recalculate the points for the rounded border and relocate the rounded rectangle to match these
        new_points = get_rectangle_points(x1=offset, y1=offset, width=new_canvas_width, height=new_canvas_height,
                                          feather=self.my_feather)
        self.canvas.coords(self.rounded_border, new_points)

    def _draw_rounded_rectangle(self, points, **kwargs):
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    @property
    def canvas_width(self) -> int:
        return self.canvas.winfo_reqwidth()

    @property
    def canvas_height(self) -> int:
        return self.canvas.winfo_reqheight()

# # Example use (WORKING)
# import tkinter
#
# from src.frontend.utils.RoundedBorder import RoundedBorder
#
# root = tkinter.Tk()
# root.withdraw()
#
# overlay = tkinter.Toplevel(root)
#
# my_rb = RoundedBorder(master=overlay)
#
#
# def update_size(_):
#     val = int(slider2.get())
#     my_rb.frame.configure(width=val, height=val)
#
#
# screen3 = tkinter.Toplevel()
# screen3.geometry(f"+{1000}+{500}")
# slider2 = tkinter.Scale(master=screen3,
#                         from_=0, to=500,
#                         orient='vertical',
#                         length=200,
#                         )
# slider2.pack()
# slider2.bind("<ButtonRelease-1>", update_size)
#
# while True:
#     root.update()
