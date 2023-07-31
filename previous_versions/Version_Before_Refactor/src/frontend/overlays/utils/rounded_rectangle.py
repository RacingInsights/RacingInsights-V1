from math import cos, sin


def create_good_rectangle(canvas, x1, y1, x2, y2, feather, res=30, color='ORANGE'):
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

    return canvas.create_polygon(points, fill=color)  # ?
