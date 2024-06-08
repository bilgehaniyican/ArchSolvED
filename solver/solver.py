import random
from math import ceil
from typing import List

from solver.corridor import Corridor
from solver.enums import Climate, RoomType
from solver.exception import UnsolvableException
from solver.room import Room
from solver.solution import Solution, get_climate_room_scores


class Solver:
    def __init__(self, floor_count: int, climate: Climate, corridors: List[Corridor], rooms: List[Room]):
        self.floor_count = floor_count
        self.climate = climate
        self.corridors = corridors
        self.rooms = rooms

    def solve(self) -> List[Solution]:
        solutions = self.create_solution()
        solutions = [solutions]

        self.ensure_vertical_circulation_exists()

        remaining_rooms = self.rooms.copy()
        room_count = 0

        for rtype in [RoomType.WC, RoomType.CLASSROOM, RoomType.CIRCULATION]:
            room_count += self.distribute(solutions, remaining_rooms, rtype)
            print("Solved", rtype, len(solutions))

        for rtype, floor in [(RoomType.COUNSELING, 1), (RoomType.GYM, 0), (RoomType.CAFE, 0), (RoomType.HEADMASTERS, 1),
                             (RoomType.MESS, self.floor_count - 1), (RoomType.AUDITORIUM, self.floor_count - 1)]:
            room_count += self.distribute_to_floor(solutions, remaining_rooms, rtype, floor)
            room_count += self.distribute_random(solutions, remaining_rooms, rtype)
            print("Solved", rtype, len(solutions))

        for rtype in [RoomType.LABORATORY, RoomType.WORKSHOP, RoomType.ADMINISTRATIVE, RoomType.TEACHERS, RoomType.HALL,
                      RoomType.LIBRARY]:
            room_count += self.distribute_random(solutions, remaining_rooms, rtype)
            print("Solved", rtype, len(solutions))

        if len(remaining_rooms) > 0:
            print("Undistributed")
            for r in remaining_rooms:
                print(r.type)

        if len(solutions) > 0:
            for side in solutions[0].sides:
                print(side.name, "floor: " + str(side.floor + 1), side.facing)
                for room in side.rooms:
                    print("    " + str(room.type))

        return solutions

    def create_solution(self) -> Solution:
        self.explode()

        solution = Solution(self.climate)

        for c in self.corridors:
            solution.draw_corridors.append(c.copy())

        for i, corridor in enumerate(self.corridors):
            a = corridor.get_a_side()
            a.name = str(i + 1) + "a"
            solution.sides.append(a)

            b = corridor.get_b_side()
            b.name = str(i + 1) + "b"
            solution.sides.append(b)

        solution.solve_conflicts()

        new_sides = []
        for side in solution.sides:
            for floor in range(self.floor_count):
                new_side = side.clone_with_floor(floor)
                new_side.name = side.name
                new_sides.append(new_side)

        solution.sides = new_sides

        return solution

    def explode(self):
        while self.explode_pass():
            pass

    def explode_pass(self):
        exploded = False
        new_corridors = list(self.corridors)

        for i, foo in enumerate(self.corridors):
            for j, bar in enumerate(self.corridors):
                if foo is bar or \
                        (foo.line.a.equals(bar.line.a) and foo.line.b.equals(bar.line.b)) or \
                        (foo.line.a.equals(bar.line.b) and foo.line.b.equals(bar.line.a)):
                    continue

                if foo.line.is_head_on(bar.line):
                    continue

                intersection_point = foo.line.calculate_intersection_point(bar.line)
                if intersection_point is None:  # Case where s and o are parallel
                    continue

                if intersection_point.equals(foo.line.a) or intersection_point.equals(foo.line.b) or \
                        intersection_point.equals(bar.line.a) or intersection_point.equals(bar.line.b):
                    continue

                if foo.line.is_point_within_bounds(intersection_point, inclusive=False):
                    x, y = foo.explode_at(intersection_point)
                    if x is not None:
                        new_corridors.append(x)
                    if y is not None:
                        new_corridors.append(y)
                    new_corridors.remove(foo)
                    exploded = True

                if bar.line.is_point_within_bounds(intersection_point, inclusive=False):
                    x, y = bar.explode_at(intersection_point)
                    if x is not None:
                        new_corridors.append(x)
                    if y is not None:
                        new_corridors.append(y)
                    self.corridors = new_corridors
                    new_corridors.remove(bar)
                    exploded = True

            if exploded:
                self.corridors = new_corridors
                return True
        return exploded


    def ensure_vertical_circulation_exists(self):
        if not self.has_intersection():
            self.insert_vertical_circulation()
        else:
            pass

    def has_intersection(self):
        for a in self.corridors:
            for b in self.corridors:
                if a is b:
                    continue

                if a.line.calculate_intersection_point(b.line) is not None:
                    return True

        return False

    def insert_vertical_circulation(self):
        # Find climate
        # Categorize sides according to best to least good to put a circulation
        # Put circulation to same side of every floor
        pass

    def distribute(self, solutions, remaining_rooms, room_type):
        rooms = get_rooms(remaining_rooms, room_type)
        rcc = len(rooms)

        if rcc == 0:
            return 0

        room = rooms[0].clone()

        rooms_per_floor = ceil(len(rooms) / self.floor_count)
        for _ in range(rooms_per_floor):
            if len(solutions) > 50000:
                return rcc

            room_count = 0
            for _a in range(self.floor_count):
                try:
                    rooms.pop()
                    room_count += 1
                except Exception:
                    break

            delete_solutions = []
            new_solutions_cumulative = []
            for solution in solutions:
                floors_sides = self.get_sides_sorted(solution, room_type)

                length = room.length

                score = -1
                for i in range(3):
                    if len(list(filter(lambda s: s.can_fit_room_by_length(length), floors_sides[0][i]))):
                        score = i
                        break

                if score == -1:
                    delete_solutions.append(solution)
                    continue

                fitting_sides = list(filter(lambda s: s.can_fit_room_by_length(length), floors_sides[0][score]))
                new_solutions = [solution.clone() for _ in range(len(fitting_sides))]

                for side, new_solution in zip(fitting_sides, new_solutions):
                    new_floor_sides = self.get_sides_sorted(new_solution, room_type)
                    name = side.name
                    for j in range(min(self.floor_count, room_count)):
                        try:
                            next(filter(lambda s: s.name == name, new_floor_sides[j][score])).insert(room.clone())
                        except Exception:
                            raise UnsolvableException

                new_solutions_cumulative.extend(new_solutions)
                delete_solutions.append(solution)

            for s in delete_solutions:
                solutions.remove(s)
            solutions.extend(new_solutions_cumulative)

        return rcc

    def get_sides_sorted(self, solution, room_type):
        scores = get_climate_room_scores(self.climate, room_type)
        floors = [[[], [], []] for i in range(self.floor_count)]

        def get_score(s):
            if scores[s.facing] == 100:
                return 0
            elif scores[s.facing] == 50:
                return 1
            else:
                return 2

        for s in solution.sides:
            floor = s.floor
            score = get_score(s)

            floors[floor][score].append(s)

        return floors

    def distribute_to_floor(self, solutions, remaining_rooms, room_type, floor):
        rooms = get_rooms(remaining_rooms, room_type)  # get rooms of type
        rcc = len(rooms)  # get room count of type

        if rcc == 0:  # back away if no rooms of type
            return 0

        length = rooms[-1].length  # all rooms of same type have the same length

        while len(rooms) > 0:  # do until all rooms of type are placed
            room = rooms.pop()  # get a room to place

            delete_solutions = []  # we might have some solutions that can't fit room, so we delete those
            for solution in solutions:
                floors_sides = self.get_sides_sorted_to_floor(solution, room_type, floor)

                score = -1
                for i in range(3):
                    sides_that_can_fit_room = list(filter(lambda s: s.can_fit_room_by_length(length), floors_sides[i]))
                    if len(sides_that_can_fit_room) != 0:
                        score = i
                        chosen_side = random.choice(sides_that_can_fit_room)
                        chosen_side.insert(room)
                        break

                if score == -1:
                    delete_solutions.append(solution)

            for s in delete_solutions:
                solutions.remove(s)

        return rcc

    def get_sides_sorted_to_floor(self, solution, room_type, floor):
        scores = get_climate_room_scores(self.climate, room_type)
        sides = [[], [], []]

        def get_score(s):
            if scores[s.facing] == 100:
                return 0
            elif scores[s.facing] == 50:
                return 1
            else:
                return 2

        for s in filter(lambda s: s.floor == floor, solution.sides):
            score = get_score(s)

            sides[score].append(s)

        return sides

    def distribute_random(self, solutions, remaining_rooms, room_type):
        rooms = get_rooms(remaining_rooms, room_type)
        rcc = len(rooms)

        if rcc == 0:
            return 0

        length = rooms[-1].length

        while len(rooms) > 0:
            room = rooms.pop()

            delete_solutions = []
            for solution in solutions:
                sides = self.get_sides_sorted_random(solution, room_type)

                score = -1
                for i in range(3):
                    sides_that_can_fit_room = list(filter(lambda s: s.can_fit_room_by_length(length), sides[i]))
                    if len(sides_that_can_fit_room) != 0:
                        score = i
                        chosen_side = random.choice(sides_that_can_fit_room)
                        chosen_side.insert(room)
                        break

                if score == -1:
                    delete_solutions.append(solution)
                    continue

            for s in delete_solutions:
                solutions.remove(s)

        return rcc

    def get_sides_sorted_random(self, solution, room_type):
        scores = get_climate_room_scores(self.climate, room_type)
        sides = [[], [], []]

        def get_score(s):
            if scores[s.facing] == 100:
                return 0
            elif scores[s.facing] == 50:
                return 1
            else:
                return 2

        for s in solution.sides:
            score = get_score(s)
            sides[score].append(s)

        return sides


def get_rooms(remaining_rooms, room_type):
    rooms = list(filter(lambda r: r.type == room_type, remaining_rooms))
    for r in rooms:
        remaining_rooms.remove(r)

    return rooms
