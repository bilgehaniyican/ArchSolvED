import json
import math

import numpy as np

from solver.room import get_climate_room_type
import solver.const as const


def arround(p):
    return round(p, 2)


class Solution:
    def __init__(self, climate, sides=None, draw_corridors=None):
        if draw_corridors is None:
            self.draw_corridors = []
        else:
            self.draw_corridors = draw_corridors

        self.climate = climate
        if sides is None:
            self.sides = []
        else:
            self.sides = sides

    def get_score(self):
        from solver.enums import ClimateRoomType, Facing

        counts = np.zeros((len(ClimateRoomType), len(Facing)))
        total_room_count = 0

        for side in self.sides:
            for room in side.rooms:
                counts[get_climate_room_type(room.type)][side.facing] += 1
                total_room_count += 1

        counts *= get_climate_scoring(self.climate)

        return counts.sum() / total_room_count

    def get_shapes(self):
        from solver.enums import RoomType, Facing
        from solver.shape import from_room, from_corridor

        color_map = load_room_color_map_from_file()

        top_floor = 0
        for side in self.sides:
            top_floor = max(side.floor + 1, top_floor)

        rooms = []
        for side in self.sides:
            lower_point = side.get_lower_point()
            other_point = side.get_other_point()

            offset = 0
            for room in side.rooms:
                shape = from_room(
                    side.floor,
                    side.get_angle(),
                    float(lower_point.x),
                    float(lower_point.y),
                    room.length,
                    room.width,
                    color_map[room.type],
                    offset
                )

                if side.a_or_b == "a":
                    new_points = []
                    for point in shape.points:
                        new_points.append(mirror(point, (lower_point.x, other_point.x, lower_point.y, other_point.y)))

                    shape.points = new_points

                shape.score = get_climate_room_scores(self.climate, room.type)[side.facing]

                rooms.append(shape)

                offset += room.length

        corridors = []
        for c in self.draw_corridors:
            for i in range(top_floor):
                corridors.append(from_corridor(
                    i,
                    c.line.a.x,
                    c.line.a.y,
                    c.line.b.x,
                    c.line.b.y,
                    color_map[RoomType.CIRCULATION]
                ))

        rooms.sort(key=lambda r: r.layer)
        corridors.sort(key=lambda c: c.layer)

        shapes = []
        shapes.extend(rooms)
        shapes.extend(corridors)

        return list(map(lambda s: s.to_dict(), shapes))

    def solve_conflicts(self):
        from solver.point import Point
        from solver.enums import Facing
        from solver.line import Line

        sides_offsets = {}
        for side in self.sides:
            line = side.line
            offset_slope = - (1 / (side.line.slope if side.line.slope != 0 else 0.00000000000001))

            x = const.PULL_DISTANCE / math.sqrt(offset_slope * offset_slope + 1)
            y = x * offset_slope
            new_line1 = Line(Point(line.a.x + x, line.a.y + y), Point(line.b.x + x, line.b.y + y))

            x = -const.PULL_DISTANCE / math.sqrt(offset_slope * offset_slope + 1)
            y = x * offset_slope
            new_line2 = Line(Point(line.a.x + x, line.a.y + y), Point(line.b.x + x, line.b.y + y))

            def get_line(side, line1, line2):
                if side.facing == Facing.KD:
                    return line1 if line1.a.x > side.line.a.x and line1.a.y < side.line.a.y else line2
                elif side.facing == Facing.K:
                    return line1 if                               line1.a.y < side.line.a.y else line2
                elif side.facing == Facing.KB:
                    return line1 if line1.a.x < side.line.a.x and line1.a.y < side.line.a.y else line2
                elif side.facing == Facing.B:
                    return line1 if line1.a.x < side.line.a.x else line2
                elif side.facing == Facing.GB:
                    return line1 if line1.a.x < side.line.a.x and line1.a.y > side.line.a.y else line2
                elif side.facing == Facing.G:
                    return line1 if                               line1.a.y > side.line.a.y else line2
                elif side.facing == Facing.GD:
                    return line1 if line1.a.x > side.line.a.x and line1.a.y > side.line.a.y else line2
                elif side.facing == Facing.D:
                    return line1 if line1.a.x > side.line.a.x else line2
                else:
                    return line1

            sides_offsets[side.name] = [side.facing, get_line(side, new_line1, new_line2), []]

        for foo_name, foo in sides_offsets.items():
            for bar_name, bar in sides_offsets.items():
                if foo is bar:
                    continue

                if foo[1].does_intersect_within_bounds(bar[1]):
                    foo[2].append(bar_name)
                    bar[2].append(foo_name)

        for foo in self.sides:
            for bar in self.sides:
                if foo is bar:
                    continue

                if round(foo.line.slope, 2) == round(bar.line.slope, 2):
                    continue

                if bar.name not in sides_offsets[foo.name][2]:
                    continue

                if foo.line.a.equals(bar.line.a) and not (foo.line.is_point_within_bounds(bar.line.b, inclusive=True) or
                                                          bar.line.is_point_within_bounds(foo.line.b, inclusive=True)):
                    foo.line.move_a_or_b_by("a", const.PULL_DISTANCE)
                    bar.line.move_a_or_b_by("a", const.PULL_DISTANCE)
                elif foo.line.a.equals(bar.line.b) and not (foo.line.is_point_within_bounds(bar.line.a, inclusive=True) or
                                                            bar.line.is_point_within_bounds(foo.line.b, inclusive=True)):
                    foo.line.move_a_or_b_by("a", const.PULL_DISTANCE)
                    bar.line.move_a_or_b_by("b", const.PULL_DISTANCE)
                elif foo.line.b.equals(bar.line.a) and not (foo.line.is_point_within_bounds(bar.line.b, inclusive=True) or
                                                            bar.line.is_point_within_bounds(foo.line.a, inclusive=True)):
                    foo.line.move_a_or_b_by("b", const.PULL_DISTANCE)
                    bar.line.move_a_or_b_by("a", const.PULL_DISTANCE)
                elif foo.line.b.equals(bar.line.b) and not (foo.line.is_point_within_bounds(bar.line.a, inclusive=True) or
                                                            bar.line.is_point_within_bounds(foo.line.a, inclusive=True)):
                    foo.line.move_a_or_b_by("b", const.PULL_DISTANCE)
                    bar.line.move_a_or_b_by("b", const.PULL_DISTANCE)

        for foo in self.sides:
            foo.length = foo.line.length
            foo.remaining = foo.length

    def clone(self):
        new_sides = []
        for s in self.sides:
            new_sides.append(s.clone())

        return Solution(self.climate, new_sides, draw_corridors=self.draw_corridors)

    def similarity(self, sol):
        shared = 0
        for side in self.sides:
            sol_side = list(filter(lambda s: s.get_full_name() == side.get_full_name(), sol.sides))[0]

            for i in range(14):
                shared += min(side.get_room_count(i), sol_side.get_room_count(i))

        return shared


def mirror(point, line):
    from math import pow

    px, py = point[0], point[1]
    x1, x2, y1, y2 = line

    m = (y2 - y1) / (x2 - x1)
    c = (x2 * y1 - x1 * y2) / (x2 - x1)
    d = (px + (py - c) * m) / (1 + pow(m, 2))

    return 2 * d - px, 2 * d * m - py + 2 * c


def get_climate_scoring(climate):
    lookup = inner_climate_scores()

    from solver.enums import ClimateRoomType
    from solver.enums import Facing

    climate_matrix = np.empty((len(ClimateRoomType), len(Facing)))
    for room in range(len(lookup[climate])):
        for facing in range(len(lookup[climate][room])):
            climate_matrix[room][facing] = lookup[climate][room][facing]

    return climate_matrix


def get_climate_room_scores(climate, room_type):
    return inner_climate_scores()[climate][get_climate_room_type(room_type)]


def inner_climate_scores():
    return [  # G GB B KB K KD D GD
        [  # COLD
            [100, 100, 50, 0, 0, 0, 50, 100],  # CLASSROOM
            [50, 50, 50, 0, 0, 0, 100, 100],  # LIBRARY
            [0, 0, 50, 100, 100, 100, 50, 0],  # LABORATORY
            [100, 100, 50, 0, 0, 0, 50, 50],  # CAFE
            [100, 100, 50, 0, 0, 0, 50, 50],  # MESS
            [0, 50, 50, 100, 100, 100, 50, 50],  # HALL
            [0, 50, 50, 100, 100, 100, 50, 50],  # GYM
            [0, 50, 50, 100, 100, 100, 50, 50],  # AUDITORIUM
            [100, 100, 50, 50, 0, 0, 50, 100],  # WORKSHOP
            [0, 0, 0, 50, 100, 50, 0, 0],  # WC
            [0, 0, 50, 100, 100, 100, 50, 0],  # CIRCULATION
            [100, 100, 50, 0, 0, 0, 50, 100],  # ADMINISTRATIVE
        ],
        [  # MILD
            [100, 100, 50, 0, 0, 0, 50, 100],  # CLASSROOM
            [50, 50, 50, 0, 0, 0, 100, 100],  # LIBRARY
            [0, 50, 50, 100, 100, 100, 50, 50],  # LABORATORY
            [100, 100, 50, 0, 0, 50, 50, 100],  # CAFE
            [100, 100, 50, 0, 0, 50, 50, 100],  # MESS
            [0, 50, 50, 100, 100, 100, 100, 50],  # HALL
            [0, 50, 50, 100, 100, 100, 100, 50],  # GYM
            [0, 50, 50, 100, 100, 100, 100, 50],  # AUDITORIUM
            [100, 100, 50, 50, 0, 0, 50, 100],  # WORKSHOP
            [0, 0, 50, 100, 100, 100, 50, 0],  # WC
            [0, 0, 50, 100, 100, 100, 50, 0],  # CIRCULATION
            [100, 100, 50, 0, 0, 50, 100, 100],  # ADMINISTRATIVE
        ],
        [  # HOT DRY
            [0, 50, 100, 50, 0, 50, 100, 50],  # CLASSROOM
            [0, 50, 100, 0, 0, 0, 100, 50],  # LIBRARY
            [100, 50, 0, 50, 100, 50, 0, 50],  # LABORATORY
            [0, 50, 50, 0, 0, 0, 100, 50],  # CAFE
            [0, 50, 50, 0, 0, 0, 100, 50],  # MESS
            [0, 50, 50, 100, 100, 100, 0, 0],  # HALL
            [0, 50, 50, 100, 100, 100, 0, 0],  # GYM
            [0, 50, 50, 100, 100, 100, 0, 0],  # AUDITORIUM
            [0, 50, 50, 50, 0, 0, 100, 100],  # WORKSHOP
            [0, 0, 0, 50, 100, 50, 0, 0],  # WC
            [0, 0, 50, 100, 100, 100, 50, 0],  # CIRCULATION
            [0, 50, 50, 0, 0, 100, 100, 100],  # ADMINISTRATIVE
        ],
        [  # HOT HUMID
            [100, 100, 0, 0, 0, 0, 50, 50],  # CLASSROOM
            [50, 50, 0, 0, 0, 50, 100, 100],  # LIBRARY
            [0, 0, 50, 100, 100, 100, 50, 0],  # LABORATORY
            [100, 50, 0, 0, 0, 0, 50, 100],  # CAFE
            [100, 50, 0, 0, 0, 0, 50, 100],  # MESS
            [0, 0, 100, 100, 100, 50, 50, 0],  # HALL
            [0, 0, 100, 100, 100, 50, 50, 0],  # GYM
            [0, 0, 100, 100, 100, 50, 50, 0],  # AUDITORIUM
            [100, 100, 50, 50, 0, 0, 50, 100],  # WORKSHOP
            [0, 0, 100, 100, 100, 50, 0, 0],  # WC
            [0, 0, 50, 100, 100, 100, 50, 0],  # CIRCULATION
            [100, 100, 0, 0, 0, 0, 50, 50],  # ADMINISTRATIVE
        ]
    ]


def load_room_color_map_from_file():
    from solver.room import get_type_from_string
    with open("colors.json", "r") as fd:
        colors = json.load(fd)

    color_map = {}
    for room_string, color_string in colors.items():
        room_type = get_type_from_string(room_string)
        color_map[room_type] = color_string

    return color_map
