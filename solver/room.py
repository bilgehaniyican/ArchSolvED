class Room:
    def __init__(self, type_string, width, length, room_type=None):
        if room_type is None:
            self.type = get_type_from_string(type_string)
        else:
            self.type = room_type

        self.width = width
        self.length = length

    def clone(self):
        return Room("", self.width, self.length, room_type=self.type)


def get_type_from_string(type_string):
    from solver.enums import RoomType

    lookup_table = {
        "classroom": RoomType.CLASSROOM,
        "library": RoomType.LIBRARY,
        "laboratory": RoomType.LABORATORY,
        "cafe": RoomType.CAFE,
        "mess": RoomType.MESS,
        "hall": RoomType.HALL,
        "gym": RoomType.GYM,
        "auditorium": RoomType.AUDITORIUM,
        "workshop": RoomType.WORKSHOP,
        "WC": RoomType.WC,
        "circulation": RoomType.CIRCULATION,
        "administrative": RoomType.ADMINISTRATIVE,
        "teacherslounge": RoomType.TEACHERS,
        "headmasters": RoomType.HEADMASTERS,
        "counseling": RoomType.COUNSELING
    }

    return lookup_table[type_string]


def get_climate_room_type(room_type):
    from solver.enums import RoomType
    from solver.enums import ClimateRoomType

    lookup_table = {
        RoomType.CLASSROOM: ClimateRoomType.CLASSROOM,
        RoomType.LIBRARY: ClimateRoomType.LIBRARY,
        RoomType.LABORATORY: ClimateRoomType.LABORATORY,
        RoomType.CAFE: ClimateRoomType.CAFE,
        RoomType.MESS: ClimateRoomType.MESS,
        RoomType.HALL: ClimateRoomType.HALL,
        RoomType.GYM: ClimateRoomType.GYM,
        RoomType.AUDITORIUM: ClimateRoomType.AUDITORIUM,
        RoomType.WORKSHOP: ClimateRoomType.WORKSHOP,
        RoomType.WC: ClimateRoomType.WC,
        RoomType.CIRCULATION: ClimateRoomType.CIRCULATION,
        RoomType.ADMINISTRATIVE: ClimateRoomType.ADMINISTRATIVE,
        RoomType.TEACHERS: ClimateRoomType.ADMINISTRATIVE,
        RoomType.HEADMASTERS: ClimateRoomType.ADMINISTRATIVE,
        RoomType.COUNSELING: ClimateRoomType.ADMINISTRATIVE
    }

    return lookup_table[room_type]
