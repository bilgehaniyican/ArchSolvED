from solver.corridor import Corridor
from solver.line import Line
from solver.point import Point

from solver.room import Room
from solver.solver import Solver


class School:
    def __init__(self, inputs):
        self.floor_count = inputs["floor_count"]

        self.corridors = []
        for line in inputs["boundaries"]["corridor"]:
            l = Line(
                Point(line[0][0], line[0][1]),
                Point(line[1][0], line[1][1])
            )
            self.corridors.append(Corridor(-1, l))

        requirements = inputs["requirements"]

        if "process" in requirements:
            requirements.pop("process")

        self.rooms = []
        for name, data in requirements.items():
            for _ in range(data["count"]):
                self.rooms.append(Room(name, data["width"], data["length"]))

        self.climate = get_climate_from_string(inputs["climate"])

    def solve(self):
        return Solver(self.floor_count, self.climate, self.corridors, self.rooms).solve()


def get_climate_from_string(climate_string):
    from solver.enums import Climate

    lookup = {
        "A": Climate.HOT_HUMID,
        "B": Climate.HOT_DRY,
        "C": Climate.MILD,
        "D": Climate.COLD
    }

    return lookup[climate_string]
