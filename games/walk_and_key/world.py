
import random
import json
import os
from typing import List, Dict, Optional, Any

class Door:
    def __init__(self, room1: 'Room', room2: 'Room', direction: str, lock: Optional[Dict] = None):
        self.room1: 'Room' = room1
        self.room2: 'Room' = room2
        self.direction: str = direction
        self.lock: Optional[Dict] = lock
    
    def is_locked(self) -> bool:
        return self.lock is not None

    def unlock(self) -> None:
        self.lock = None

    def get_lock_description(self) -> str:
        if self.lock:
            return f"The door is locked with a {self.lock['name']}. {self.lock['description']}"
        return "The door is unlocked."

class Room:
    def __init__(self, name: str, room_type: str, size: int, adjectives: List[str]):
        self.name: str = name
        self.room_type: str = room_type
        self.size: int = size
        self.adjectives: List[str] = adjectives
        self.doors: Dict[str, Door] = {}
        self.items: List[Dict] = []

    def add_door(self, direction: str, door: Door) -> None:
        self.doors[direction] = door

    def add_item(self, item: Dict) -> None:
        self.items.append(item)

    def remove_item(self, item: Dict) -> None:
        self.items.remove(item)

    def get_size_description(self) -> str:
        if self.size <= 2:
            return "tiny"
        elif self.size <= 4:
            return "small"
        elif self.size <= 6:
            return "medium-sized"
        elif self.size <= 8:
            return "large"
        else:
            return "enormous"

class Graph:
    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.doors: List[Door] = []

    def add_room(self, room: Room) -> None:
        self.rooms[room.name] = room

    def add_door(self, room1_name: str, room2_name: str, direction: str, lock: Optional[Dict] = None) -> None:
        room1 = self.rooms[room1_name]
        room2 = self.rooms[room2_name]
        opposite_direction = {
            "north": "south",
            "south": "north",
            "east": "west",
            "west": "east"
        }
        door = Door(room1, room2, direction, lock)
        room1.add_door(direction, door)
        room2.add_door(opposite_direction[direction], door)
        self.doors.append(door)

def generate_random_graph(num_rooms: int, min_connections: int = 1, max_connections: int = 4) -> Graph:
    world = Graph()
    room_names = [f"Room {i+1}" for i in range(num_rooms)]
    
    # Create rooms
    for room_name in room_names:
        room = Room(room_name, "generic", 0, [])  # We'll set the room type, size, and adjectives in decorate_graph
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
        room_type = random.choice(room_types)
        room.room_type = room_type["name"]
        room.adjectives = room_type["adjectives"]
        room.name = f"{random.choice(room.adjectives).capitalize()} {room.room_type.replace('_', ' ').title()}"
        room.size = room_type["size"]

    # Add locks to doors
    for door in graph.doors:
        if random.random() < 0.3:  # 30% chance of a lock, you can adjust this probability
            lock = random.choice(locks)
            door.lock = lock

    # Add keys and other items to rooms
    all_items = keys + [{"name": "Mysterious Object", "adjectives": ["intriguing", "odd", "peculiar"], "description": "An object of unknown origin and purpose."}]
    
    for room in graph.rooms.values():
        num_items = random.randint(0, 2)  # Each room can have 0 to 2 items
        for _ in range(num_items):
            matching_items = [item for item in all_items if any(adj in room.adjectives for adj in item["adjectives"])]
            if matching_items:
                item = random.choice(matching_items)
                if "count" in item:
                    item["count"] -= 1
                    if item["count"] == 0:
                        all_items.remove(item)
                room.add_item(item)

    # Ensure all locks have corresponding keys in the world
    for door in graph.doors:
        if door.lock:
            matching_key = next((key for key in keys if key["color"] == door.lock["color"]), None)
            if matching_key:
                random_room = random.choice(list(graph.rooms.values()))
                random_room.add_item(matching_key)

def generate_world(num_rooms: int, room_types_file: str, locks_file: str, keys_file: str) -> Graph:
    graph = generate_random_graph(num_rooms)
    decorate_graph(graph, room_types_file, locks_file, keys_file)
    return graph
