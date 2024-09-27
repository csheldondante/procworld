
import random
import json
import os
from typing import List, Dict, Optional, Any
from rich.text import Text
from games.walk_and_key.item import Item

from utils.gui.display_interface import show_narrative_text
from rich.text import Text
from rich.panel import Panel

import networkx as nx
from texttable import Texttable

class Lock:
    def __init__(self, name: str, color: str, adjectives: List[str], description: str):
        self.name: str = name
        self.color: str = color
        self.adjectives: List[str] = adjectives
        self.description: str = description

    def get_name(self) -> Text:
        return Text(self.name, style=f"bold {self.color}")

    def get_description(self) -> Text:
        description = Text()
        description.append(self.description)
        # Add adjectives
        if self.adjectives:
            description.append(" ")
            description.append(" ".join(self.adjectives), style="italic")
        return description

class Door:
    def __init__(self, room1: 'Room', room2: 'Room', direction: str, lock: Optional[Lock] = None):
        self.room1: 'Room' = room1
        self.room2: 'Room' = room2
        self.direction: str = direction
        self.lock: Optional[Lock] = lock
    
    def is_locked(self) -> bool:
        return self.lock is not None

    def unlock(self) -> None:
        self.lock = None

    def get_lock_description_short(self) -> Text:
        if self.lock:
            description = Text()
            description.append("Locked with a ")
            description.append(self.lock.name, style=f"bold {self.lock.color}")
            return description
        return Text("Unlocked")

    def get_lock_description(self) -> Text:
        if self.lock:
            description = Text()
            description.append("The door is locked with a ")
            description.append(self.lock.name, style=f"bold {self.lock.color}")
            description.append(f". {self.lock.description}")
            return description
        return Text("The door is unlocked.")

class Room:
    def __init__(self, name: str, room_type: str, size: int, adjectives: List[str], description: str, x: int = -1, y: int = -1):
        self.name: str = name
        self.room_type: str = room_type
        self.size: int = size
        self.adjectives: List[str] = adjectives
        self.description: str = description
        self.doors: Dict[str, Door] = {}
        self.items: List[Item] = []
        self.x: int = x
        self.y: int = y

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
        description.append(self.get_name())
        description.append(" (")
        
        # Handle adjectives
        if self.adjectives:
            adj_text = Text(", ").join([Text(adj, style="italic") for adj in self.adjectives])
            description.append(adj_text)
            description.append(", ")
        
        description.append(self.get_size_description())
        description.append(").\n\n")
        description.append(self.description)
        description.append("\n\n")

        if self.items:
            description.append("Items in the room:\n")
            for item in self.items:
                description.append("- ")
                description.append(item.get_full_description())
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

def generate_random_graph(num_rooms: int) -> Graph:
    world = Graph()
    grid_size = 5
    grid = [[None for _ in range(grid_size)] for _ in range(grid_size)]
    
    # Create rooms and place them on the grid
    for i in range(num_rooms):
        room_name = f"Room {i+1}"
        
        # Find an empty cell on the grid
        while True:
            x, y = random.randint(0, grid_size-1), random.randint(0, grid_size-1)
            if grid[y][x] is None:
                room = Room(room_name, room_type="generic", size=0, adjectives=[], description="", x=x, y=y)
                world.add_room(room)
                grid[y][x] = room
                break
    
    # Create connections
    directions = ["north", "south", "east", "west"]
    for y in range(grid_size):
        for x in range(grid_size):
            if grid[y][x] is not None:
                room = grid[y][x]
                for direction in directions:
                    if direction == "north" and y > 0 and grid[y-1][x] is not None:
                        world.add_door(room.name, grid[y-1][x].name, direction)
                    elif direction == "south" and y < grid_size-1 and grid[y+1][x] is not None:
                        world.add_door(room.name, grid[y+1][x].name, direction)
                    elif direction == "east" and x < grid_size-1 and grid[y][x+1] is not None:
                        world.add_door(room.name, grid[y][x+1].name, direction)
                    elif direction == "west" and x > 0 and grid[y][x-1] is not None:
                        world.add_door(room.name, grid[y][x-1].name, direction)
    
    return world

def load_json(file_path: str) -> Any:
    full_path = os.path.join(os.path.dirname(__file__), file_path)
    # print("Loading...", full_path)
    with open(full_path, 'r') as f:
        return json.load(f)

def decorate_graph(graph: Graph, room_types_file: str, locks_file: str, keys_file: str) -> None:
    room_types = load_json(room_types_file)
    locks_data = load_json(locks_file)
    keys = load_json(keys_file)

    # Assign room types and ensure unique names
    room_name_counts = {}
    for room in graph.rooms.values():
        room_type = random.choice(room_types)
        room.room_type = room_type["name"]
        room.adjectives = room_type["adjectives"][:3]  # Take the first 3 adjectives
        base_name = f"{room.room_type.replace('_', ' ').title()}"
        
        if base_name in room_name_counts:
            room_name_counts[base_name] += 1
            count = room_name_counts[base_name]
            if count <= len(room.adjectives):
                room.name = f"{room.adjectives[count-1].capitalize()} {base_name}"
            else:
                room.name = f"{base_name} {count}"
        else:
            room_name_counts[base_name] = 1
            room.name = base_name
        
        room.size = room_type["size"]
        room.description = room_type["description"]

    # Create Lock objects
    locks = [Lock(lock["name"], lock["color"], lock["adjectives"], lock["description"]) for lock in locks_data]

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
            matching_key = next((key for key in all_items if key.color == door.lock.color), None)
            if matching_key:
                random_room = random.choice(list(graph.rooms.values()))
                random_room.add_item(matching_key)
                all_items.remove(matching_key)

def generate_world(num_rooms: int, room_types_file: str, locks_file: str, keys_file: str) -> Graph:
    graph = generate_random_graph(min(num_rooms, 25))  # Limit to 25 rooms (5x5 grid)
    decorate_graph(graph, room_types_file, locks_file, keys_file)
    return graph


def print_map(graph: Graph) -> None:
    map_text = Text()

    # Calculate grid size based on room positions
    min_x = min(room.x for room in graph.rooms.values())
    max_x = max(room.x for room in graph.rooms.values())
    min_y = min(room.y for room in graph.rooms.values())
    max_y = max(room.y for room in graph.rooms.values())
    
    grid_width = max_x - min_x + 1
    grid_height = max_y - min_y + 1

    # Create a grid representation
    grid = [[None for _ in range(grid_width)] for _ in range(grid_height)]
    for room in graph.rooms.values():
        grid[room.y - min_y][room.x - min_x] = room

    # Print the grid
    map_text.append("Grid Map:\n")
    cell_size = 16
    for row in grid:
        for room in row:
            if room:
                map_text.append(f"[{room.name[:cell_size-2]:^{cell_size}}]")
            else:
                map_text.append("[" + " " * cell_size + "]")
        map_text.append("\n")
    map_text.append("\n")

    # Print detailed room information
    map_text.append("Room Details:\n")
    for room_name, room in graph.rooms.items():
        map_text.append(room.get_name())
        map_text.append("\n")

        # Items
        for item in room.items:
            map_text.append("  Contains: ")
            map_text.append(item.get_name())
            map_text.append("\n")

        # Doors
        for direction, door in room.doors.items():
            target_room = door.room2 if door.room1 == room else door.room1
            door_text = Text(f"  {direction.capitalize()}: ")
            door_text.append(target_room.get_name())
            
            if door.is_locked():
                door_text.append(" (Locked with ")
                door_text.append(door.lock.get_name())
                door_text.append(")")
            
            door_text.append("\n")
            map_text.append(door_text)
        if not room.doors:
            map_text.append("  Not connected!\n")

        map_text.append("\n")

    show_narrative_text(map_text, "World Map (development only)")
