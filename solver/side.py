from solver.enums import Facing
from solver.line import Line
from solver.point import Point


class Side:
    def __init__(self, floor, a_or_b, length, line, corridor_tilt=None, facing=None, rooms=None, remaining=None,
                 name=None):
        self.a_or_b = a_or_b

        if corridor_tilt is not None:
            self.facing = get_facing_from_ab_and_tilt(a_or_b, corridor_tilt)
        elif facing is not None:
            self.facing = facing

        self.length = length
        self.floor = floor
        self.line = line

        if rooms is None:
            self.rooms = []
        else:
            self.rooms = rooms

        if remaining is None:
            self.remaining = self.length
        else:
            self.remaining = remaining

        if name is None:
            self.name = ""
        else:
            self.name = name

    def clone_with_floor(self, floor):
        return Side(floor, self.a_or_b, self.length, self.line.copy(), facing=self.facing)

    def clone(self):
        new_rooms = []
        for r in self.rooms:
            new_rooms.append(r.clone())

        return Side(self.floor, self.a_or_b, self.length, self.line.copy(), facing=self.facing,
                    remaining=self.remaining, rooms=new_rooms, name=self.name)

    def insert(self, room):
        if room.length <= self.remaining:
            self.rooms.append(room)
            self.remaining -= room.length

            return True
        else:
            return False

    def get_angle(self):
        return self.line.calculate_angle()

    def get_lower_point(self):
        if self.line.a.y < self.line.b.y:
            return self.line.a
        else:
            return self.line.b

    def get_other_point(self):
        if self.line.a.y > self.line.b.y:
            return self.line.a
        else:
            return self.line.b

    def can_fit_room_by_length(self, length):
        return length < self.remaining

    def is_point_within_bounds(self, point, inclusive=False):
        return self.line.is_point_within_bounds(point, inclusive)

    def move_a_or_b_by(self, a_or_b, length):
        self.line.move_a_or_b_by(a_or_b, length)

    def __str__(self):
        return "{} = {}".format(self.name, self.line)

    def get_room_count(self, room_type):
        return len(list(filter(
            lambda r: r.type == room_type,
            self.rooms
        )))

    def get_full_name(self):
        return str(self.floor) + "_" + self.name


def get_facing_from_ab_and_tilt(a_or_b, corridor_tilt):
    from solver.enums import Tilt
    from solver.enums import Facing

    lookup_table = {
        "a": {
            Tilt.FLAT: Facing.G,
            Tilt.RIGHT: Facing.GD,
            Tilt.PERPENDICULAR: Facing.D,
            Tilt.LEFT: Facing.KD,
            Tilt.OTHER_FLAT: Facing.K
        },
        "b": {
            Tilt.FLAT: Facing.K,
            Tilt.RIGHT: Facing.KB,
            Tilt.PERPENDICULAR: Facing.B,
            Tilt.LEFT: Facing.GB,
            Tilt.OTHER_FLAT: Facing.G
        }
    }

    return lookup_table[a_or_b][corridor_tilt]
