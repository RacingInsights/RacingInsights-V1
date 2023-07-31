import tkinter
from math import cos, sin


def _get_rectangle_points(x1, y1, width, height, feather, res=10):
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


root = tkinter.Tk()

canvas = tkinter.Canvas(master=root, bg="RED", width=500, height=500)
canvas.pack()

center_x = canvas.winfo_reqwidth() // 2
center_y = canvas.winfo_reqheight() // 2
print(center_x, center_y)

frame = tkinter.Frame(width=300, height=300, bg="BLUE")
window = canvas.create_window(center_x, center_y, anchor="center", window=frame)

points = _get_rectangle_points(x1=0, y1=0,
                               width=canvas.winfo_reqwidth(),
                               height=canvas.winfo_reqheight(),
                               feather=22)


def _draw_rounded_rectangle(points_, **kwargs):
    return canvas.create_polygon(points_, smooth=True, **kwargs)


rounded_rectangle = _draw_rounded_rectangle(points_=points, fill="GREEN")


def center_frame(_):
    resize_canvas(_)
    h_canvas_width = canvas.winfo_reqwidth() // 2
    h_canvas_height = canvas.winfo_reqheight() // 2
    canvas.coords(window, h_canvas_width, h_canvas_height)
    points = _get_rectangle_points(x1=0, y1=0, width=2 * h_canvas_width, height=2 * h_canvas_height,
                                   feather=40)
    canvas.coords(rounded_rectangle, points)


frame.bind("<Configure>", center_frame)


def resize_canvas(_):
    width = frame.winfo_reqwidth() + 100
    height = frame.winfo_reqheight() + 100
    canvas.configure(width=width, height=height)


def update_size(_):
    val = int(slider2.get())
    frame.configure(width=val, height=val)


screen3 = tkinter.Toplevel()
screen3.geometry(f"+{1000}+{500}")
slider2 = tkinter.Scale(master=screen3,
                        from_=0, to=500,
                        orient='vertical',
                        length=200,
                        )
slider2.pack()
slider2.bind("<ButtonRelease-1>", update_size)

while True:
    root.update()
