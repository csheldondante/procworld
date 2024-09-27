
import random
import json
import os
from typing import List, Dict, Optional, Any
from rich.text import Text
from games.walk_and_key.item import Item

from utils.gui.display_interface import show_narrative_text
from rich.text import Text
from rich.panel import Panel

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

    def get_lock_description_short(self) -> Text:
        if self.lock:
            description = Text()
            description.append("Locked with a ")
            description.append(self.lock['name'], style=f"bold {self.lock['color']}")
            return description
        return Text("Unlocked")

    def get_lock_description(self) -> Text:
        if self.lock:
            description = Text()
            description.append("The door is locked with a ")
            description.append(self.lock['name'], style=f"bold {self.lock['color']}")
            description.append(f". {self.lock['description']}")
            return description
        return Text("The door is unlocked.")

class Room:
    def __init__(self, name: str, room_type: str, size: int, adjectives: List[str]):
        self.name: str = name
        self.room_type: str = room_type
        self.size: int = size
        self.adjectives: List[str] = adjectives
        self.doors: Dict[str, Door] = {}
        self.items: List[Item] = []

    def add_door(self, direction: str, door: Door) -> None:
        self.doors[direction] = door

    def add_item(self, item: Item) -> None:
        self.items.append(item)

    def remove_item(self, item: Item) -> None:
        self.items.remove(item)

    def get_name(self) -> Text:
        return Text(self.name, style="bold")

    def get_size_description(self) -> Text:
        if self.size <= 2:
            return Text("tiny")
        elif self.size <= 4:
            return Text("small")
        elif self.size <= 6:
            return Text("medium-sized")
        elif self.size <= 8:
            return Text("large")
        else:
            return Text("enormous")

    def get_full_description(self) -> Text:
        description = Text()
        description.append("You are in the ")
        description.append(self.get_size_description())
        description.append(" ")
        description.append(self.get_name())
        description.append(".\n\n")

        if self.items:
            description.append("Items in the room:\n")
            for item in self.items:
                description.append("- ")
                description.append(item.get_name())
                description.append("\n")
        else:
            description.append("There are no items in this room.\n")

        return description

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
    # print("Loading...", full_path)
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
    all_items = [Item(key["name"], key["color"], key["adjectives"], key["description"]) for key in keys]
    all_items.append(Item("Mysterious Object", "gray", ["intriguing", "odd", "peculiar"], "An object of unknown origin and purpose."))
    
    for room in graph.rooms.values():
        num_items = random.randint(0, 2)  # Each room can have 0 to 2 items
        for _ in range(num_items):
            matching_items = [item for item in all_items if any(adj in room.adjectives for adj in item.adjectives)]
            if matching_items:
                item = random.choice(matching_items)
                room.add_item(item)
                all_items.remove(item)

    # Ensure all locks have corresponding keys in the world
    for door in graph.doors:
        if door.lock:
            matching_key = next((key for key in all_items if key.color == door.lock["color"]), None)
            if matching_key:
                random_room = random.choice(list(graph.rooms.values()))
                random_room.add_item(matching_key)
                all_items.remove(matching_key)

def generate_world(num_rooms: int, room_types_file: str, locks_file: str, keys_file: str) -> Graph:
    graph = generate_random_graph(num_rooms)
    decorate_graph(graph, room_types_file, locks_file, keys_file)
    return graph

def print_map(graph: Graph) -> None:
    map_text = Text()

    for room_name, room in graph.rooms.items():
        room_text = Text()
        room_text.append(room.get_name())
        room_text.append("\n")

        for direction, door in room.doors.items():
            target_room = door.room2 if door.room1 == room else door.room1
            door_text = Text(f"  {direction.capitalize()}: ")
            door_text.append(target_room.get_name())
            
            if door.is_locked():
                door_text.append(" (")
                door_text.append(Text("Locked", style=f"bold {door.lock['color']}"))
                door_text.append(")")
            
            room_text.append(door_text)
            room_text.append("\n")

        panel = Panel(room_text, expand=False, border_style="cyan")
        map_text.append(panel)
        map_text.append("\n")

    show_narrative_text(map_text, "World Map")
