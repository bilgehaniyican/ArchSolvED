class Shape:
    def __init__(self, layer, points, color):
        self.layer = layer
        self.points = points
        self.color = color
        self.score = 0

    def to_dict(self):
        return {
            "layer": self.layer,
            "points": self.points,
            "color": self.color,
            "score": self.score,
        }


def from_room(layer, angle, x, y, length, width, color, offset):
    return Shape(layer, get_points(angle, x, y, length, width, offset), color)


def from_corridor(layer, x1, y1, x2, y2, color):
    return Shape(layer, [(x1, y1), (x2, y2)], color)


def get_points(angle, x, y, length, width, offset):
    from math import sin, cos

    xp, yp = x + offset * cos(angle), y + offset * sin(angle)

    wxc = width * cos(angle)
    wyc = width * sin(angle)
    lxc = length * sin(angle)  # width * cos(90 - angle)
    lyc = length * cos(angle)  # width * sin(90 - angle)

    return [
        (xp, yp),
        rotate([xp, yp], [xp + wxc, yp + wyc]),
        rotate([xp, yp], [xp + wxc - lxc, yp + wyc + lyc]),
        rotate([xp, yp], [xp - lxc, yp + lyc]),
    ]


def rotate(origin, point):
    from math import cos, sin, pi

    ox, oy = origin[0], origin[1]
    px, py = point[0], point[1]
    angle = - pi / 2

    qx = ox + cos(angle) * (px - ox) - sin(angle) * (py - oy)
    qy = oy + sin(angle) * (px - ox) + cos(angle) * (py - oy)

    return qx, qy
