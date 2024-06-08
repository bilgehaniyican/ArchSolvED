def arround(a):
    return round(a, 1)


class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def distance_from(self, point) -> float:
        from math import sqrt, pow

        return sqrt(
            pow(point.x - self.x, 2) + pow(point.y - self.y, 2)
        )

    def equals(self, p):
        return arround(self.x) == arround(p.x) and arround(self.y) == arround(p.y)

    def copy(self):
        return Point(self.x, self.y)

    def __str__(self):
        return "({}, {})".format(round(self.x, 2), round(self.y, 2))
