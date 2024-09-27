
import random
import json
import os
from typing import List, Dict, Optional, Any

class Door:
    def __init__(self, room1: 'Room', room2: 'Room', direction: str, lock_color: Optional[str] = None):
        self.room1: 'Room' = room1
        self.room2: 'Room' = room2
        self.direction: str = direction
        self.lock_color: Optional[str] = lock_color

class Room:
    def __init__(self, name: str, room_type: str):
        self.name: str = name
        self.room_type: str = room_type
        self.doors: Dict[str, Door] = {}
        self.items: List[str] = []

    def add_door(self, direction: str, door: Door) -> None:
        self.doors[direction] = door

    def add_item(self, item: str) -> None:
        self.items.append(item)

    def remove_item(self, item: str) -> None:
        self.items.remove(item)

class Graph:
    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.doors: List[Door] = []

    def add_room(self, room: Room) -> None:
        self.rooms[room.name] = room

    def add_door(self, room1_name: str, room2_name: str, direction: str, lock_color: Optional[str] = None) -> None:
        room1 = self.rooms[room1_name]
        room2 = self.rooms[room2_name]
        opposite_direction = {
            "north": "south",
            "south": "north",
            "east": "west",
            "west": "east"
        }
        door = Door(room1, room2, direction, lock_color)
        room1.add_door(direction, door)
        room2.add_door(opposite_direction[direction], door)
        self.doors.append(door)

def generate_random_graph(num_rooms: int, min_connections: int = 1, max_connections: int = 4) -> Graph:
    world = Graph()
    room_names = [f"Room {i+1}" for i in range(num_rooms)]
    
    # Create rooms
    for room_name in room_names:
        room = Room(room_name, "generic")  # We'll set the room type in decorate_graph
        world.add_room(room)
    
    # Create connections
    for room_name in room_names:
        num_connections = random.randint(min_connections, min(max_connections, num_rooms - 1))
        connected_rooms = random.sample([r for r in room_names if r != room_name], num_connections)
        
        for connected_room in connected_rooms:
            if connected_room not in [door.room2.name for door in world.rooms[room_name].doors.values()]:
                direction = random.choice(["north", "south", "east", "west"])
                world.add_door(room_name, connected_room, direction)
    
    return world

def load_json(file_path: str) -> Any:
    full_path = os.path.join(os.path.dirname(__file__), file_path)
    with open(full_path, 'r') as f:
        return json.load(f)

def decorate_graph(graph: Graph, room_types_file: str, locks_file: str, keys_file: str) -> None:
    room_types = load_json(room_types_file)
    locks = load_json(locks_file)
    keys = load_json(keys_file)

    # Assign room types
    for room in graph.rooms.values():
        room.room_type = random.choice(list(room_types.keys()))

    # Add items to rooms based on room type
    for room in graph.rooms.values():
        items = room_types[room.room_type]["items"]
        num_items = random.randint(items["min"], items["max"])
        for _ in range(num_items):
            item = random.choice(items["possible"])
            room.add_item(item)

    # Add locks to doors
    for door in graph.doors:
        if random.random() < locks["probability"]:
            lock_color = random.choice(locks["colors"])
            door.lock_color = lock_color

    # Add keys to rooms
    for key_color, key_info in keys.items():
        for _ in range(key_info["count"]):
            room = random.choice(list(graph.rooms.values()))
            room.add_item(f"{key_color.capitalize()} Key")

def generate_world(num_rooms: int, room_types_file: str, locks_file: str, keys_file: str) -> Graph:
    graph = generate_random_graph(num_rooms)
    decorate_graph(graph, room_types_file, locks_file, keys_file)
    return graph
