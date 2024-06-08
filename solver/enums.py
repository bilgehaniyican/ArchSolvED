from enum import IntEnum


class Tilt(IntEnum):
    FLAT = 0
    RIGHT = 1
    PERPENDICULAR = 2
    LEFT = 3
    OTHER_FLAT = 4


class RoomType(IntEnum):
    CLASSROOM = 0
    LIBRARY = 1
    LABORATORY = 2
    CAFE = 3
    MESS = 4
    HALL = 5
    GYM = 6
    AUDITORIUM = 7
    WORKSHOP = 8
    WC = 9
    CIRCULATION = 10
    HEADMASTERS = 11
    ADMINISTRATIVE = 12
    TEACHERS = 13
    COUNSELING = 14


class ClimateRoomType(IntEnum):
    CLASSROOM = 0
    LIBRARY = 1
    LABORATORY = 2
    CAFE = 3
    MESS = 4
    HALL = 5
    GYM = 6
    AUDITORIUM = 7
    WORKSHOP = 8
    WC = 9
    CIRCULATION = 10
    ADMINISTRATIVE = 11


class Facing(IntEnum):
    G = 0
    GB = 1
    B = 2
    KB = 3
    K = 4
    KD = 5
    D = 6
    GD = 7


class Climate(IntEnum):
    COLD = 0
    MILD = 1
    HOT_DRY = 2
    HOT_HUMID = 3
