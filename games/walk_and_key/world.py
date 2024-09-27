
import random

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

def generate_random_graph(num_rooms, min_connections=1, max_connections=4):
    world = Graph()
    room_names = [f"Room {i+1}" for i in range(num_rooms)]
    
    # Create rooms
    for room_name in room_names:
        world.add_room(Room(room_name))
    
    # Create connections
    for room_name in room_names:
        num_connections = random.randint(min_connections, min(max_connections, num_rooms - 1))
        connected_rooms = random.sample([r for r in room_names if r != room_name], num_connections)
        
        for connected_room in connected_rooms:
            if connected_room not in world.rooms[room_name].doors.values():
                direction = random.choice(["north", "south", "east", "west"])
                world.add_door(room_name, connected_room, direction)
    
    return world
