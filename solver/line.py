from solver.point import Point


def arround(p):
    return Point(round(p.x, 1), round(p.y, 1))


class Line:
    def __init__(self, a, b):
        self.a = a
        self.b = b
        self.length = self.a.distance_from(self.b)
        self.slope, self.offset = self.calculate_slope_and_offset()

    def calculate_cosine(self):
        if self.a.y < self.b.y:
            adjacent = self.b.x - self.a.x
            opposite = self.b.y - self.a.y
        else:
            adjacent = self.a.x - self.b.x
            opposite = self.a.y - self.b.y

        hypotenuse = self.length

        return adjacent / hypotenuse * (-1 if opposite < 0 else 1)

    def calculate_angle(self):
        from math import acos

        return acos(self.calculate_cosine())

    def copy(self):
        return Line(self.a.copy(), self.b.copy())

    def calculate_slope_and_offset(self):
        if self.a.x == self.b.x:
            return None, None

        slope = (self.b.y - self.a.y) / (self.b.x - self.a.x)
        offset = self.a.y - slope * self.a.x

        return slope, offset

    def does_intersect_within_bounds(self, line):
        intersection = self.calculate_intersection_point(line)
        if intersection is None:
            return False

        return self.is_point_within_bounds(intersection, True) and line.is_point_within_bounds(intersection, True)

    def calculate_intersection_point(self, line):
        if self.slope is None and line.slope is None:
            return None  # Two parallel lines, perpendicular to x axis
        elif self.slope is None:
            x = self.a.x
            y = line.slope * x + line.offset
        elif line.slope is None:
            x = line.a.x
            y = self.slope * x + self.offset
        else:
            if round(self.slope, 1) == round(line.slope, 1):
                return None

            x = (line.offset - self.offset) / (self.slope - line.slope)
            y = self.slope * x + self.offset

        return Point(x, y)

    def is_point_within_bounds(self, point, inclusive):
        dist_a = self.a.distance_from(point)
        dist_b = self.b.distance_from(point)

        if dist_a < 0.1 or dist_b < 0.1:
            return False

        a = arround(self.a)
        b = arround(self.b)
        p = arround(point)

        if inclusive:
            xa = a.x <= p.x <= b.x
            xb = a.x >= p.x >= b.x
            ya = a.y <= p.y <= b.y
            yb = a.y >= p.y >= b.y
        else:
            xa = a.x < p.x < b.x
            xb = a.x > p.x > b.x
            ya = a.y < p.y < b.y
            yb = a.y > p.y > b.y

        return (xa or xb) and (ya or yb)

    def is_head_on(self, line):
        return self.a.equals(line.a) or self.a.equals(line.b) or self.b.equals(line.a) or self.b.equals(line.b)

    def move_a_or_b_by(self, a_or_b, length):
        if a_or_b == "a":
            dx = (self.b.x - self.a.x) / self.length * length
            dy = (self.b.y - self.a.y) / self.length * length
        else:
            dx = (self.a.x - self.b.x) / self.length * length
            dy = (self.a.y - self.b.y) / self.length * length

        if a_or_b == "a":
            self.a.x += dx
            self.a.y += dy
        else:
            self.b.x += dx
            self.b.y += dy

        self.length = self.a.distance_from(self.b)
        self.slope, self.offset = self.calculate_slope_and_offset()

    def __str__(self):
        return "{} > {} ({})".format(self.a, self.b, self.length)
