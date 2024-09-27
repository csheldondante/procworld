class Room:
    def __init__(self, name):
        self.name = name
        self.doors = {}

    def add_door(self, direction, room):
        self.doors[direction] = room

class Graph:
    def __init__(self):
        self.rooms = {}

    def add_room(self, room):
        self.rooms[room.name] = room

    def add_door(self, room1_name, room2_name, direction):
        room1 = self.rooms[room1_name]
        room2 = self.rooms[room2_name]
        opposite_direction = {
            "north": "south",
            "south": "north",
            "east": "west",
            "west": "east"
        }
        room1.add_door(direction, room2)
        room2.add_door(opposite_direction[direction], room1)
