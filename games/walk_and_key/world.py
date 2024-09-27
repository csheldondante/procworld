
import random

class Door:
    def __init__(self, room1, room2, direction, is_locked=False):
        self.room1 = room1
        self.room2 = room2
        self.direction = direction
        self.is_locked = is_locked

class Room:
    def __init__(self, name):
        self.name = name
        self.doors = {}
        self.items = []

    def add_door(self, direction, door):
        self.doors[direction] = door

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        self.items.remove(item)

class Graph:
    def __init__(self):
        self.rooms = {}
        self.doors = []

    def add_room(self, room):
        self.rooms[room.name] = room

    def add_door(self, room1_name, room2_name, direction, is_locked=False):
        room1 = self.rooms[room1_name]
        room2 = self.rooms[room2_name]
        opposite_direction = {
            "north": "south",
            "south": "north",
            "east": "west",
            "west": "east"
        }
        door = Door(room1, room2, direction, is_locked)
        room1.add_door(direction, door)
        room2.add_door(opposite_direction[direction], door)
        self.doors.append(door)

def generate_random_graph(num_rooms, min_connections=1, max_connections=4, locked_door_probability=0.2):
    world = Graph()
    room_names = [f"Room {i+1}" for i in range(num_rooms)]
    
    # Create rooms
    for room_name in room_names:
        room = Room(room_name)
        world.add_room(room)
        
        # Add random items to the room
        num_items = random.randint(0, 2)
        for _ in range(num_items):
            item = random.choice(["Key", "Coin", "Gem", "Book", "Potion"])
            room.add_item(item)
    
    # Create connections
    for room_name in room_names:
        num_connections = random.randint(min_connections, min(max_connections, num_rooms - 1))
        connected_rooms = random.sample([r for r in room_names if r != room_name], num_connections)
        
        for connected_room in connected_rooms:
            if connected_room not in [door.room2.name for door in world.rooms[room_name].doors.values()]:
                direction = random.choice(["north", "south", "east", "west"])
                is_locked = random.random() < locked_door_probability
                world.add_door(room_name, connected_room, direction, is_locked)
    
    return world
