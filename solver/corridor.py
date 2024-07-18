class Corridor:
    def __init__(self, floor, line):
        self.line = line

        cosine = self.line.calculate_cosine()
        self.tilt = get_tilt_from_cosine(cosine)
        self.length = self.line.length

        self.floor = floor

    def get_a_side(self):
        from solver.side import Side

        return Side(self.floor, "a", self.length, self.line.copy(), corridor_tilt=self.tilt)

    def get_b_side(self):
        from solver.side import Side

        return Side(self.floor, "b", self.length, self.line.copy(), corridor_tilt=self.tilt)

    def copy(self):
        return Corridor(self.floor, self.line.copy())

    def explode_at(self, point):
        from solver.line import Line
        from solver.point import Point

        x = Corridor(self.floor, Line(Point(self.line.a.x, self.line.a.y), Point(point.x, point.y)))
        y = Corridor(self.floor, Line(Point(point.x, point.y), Point(self.line.b.x, self.line.b.y)))

        from const import PULL_DISTANCE

        if x.line.length < PULL_DISTANCE:
            x = None

        if y.line.length < PULL_DISTANCE:
            y = None

        return x, y


def get_tilt_from_cosine(cosine):
    from solver.enums import Tilt

    if 1 >= cosine > 0.92387953251:
        return Tilt.FLAT
    elif 0.92387953251 >= cosine > 0.38268343236:
        return Tilt.RIGHT
    elif 0.38268343236 >= cosine > -0.38268343236:
        return Tilt.PERPENDICULAR
    elif -0.38268343236 >= cosine > -0.92387953251:
        return Tilt.LEFT
    elif -0.92387953251 >= cosine >= -1:
        return Tilt.OTHER_FLAT
