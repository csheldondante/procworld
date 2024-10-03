import random
from rich.text import Text

from games.walk_and_key.core_lock_and_key import dynamic_decorate_graph
from games.walk_and_key.graph import Graph
from games.walk_and_key.item import Item
from games.walk_and_key.room_and_door import Room
from games.walk_and_key.lock import Lock
from games.walk_and_key.utils.json import load_json
from games.walk_and_key.voronoi_graph_generator import get_voronoi_graph
from scipy.spatial import Voronoi
import numpy as np

from utils.gui.display_interface import show_narrative_text, show_error


def generate_random_graph(num_rooms: int, grid_size: int) -> Graph:
    world = Graph()
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
                        world.add_door(room, grid[y-1][x], direction)
                    elif direction == "south" and y < grid_size-1 and grid[y+1][x] is not None:
                        world.add_door(room, grid[y+1][x], direction)
                    elif direction == "east" and x < grid_size-1 and grid[y][x+1] is not None:
                        world.add_door(room, grid[y][x+1], direction)
                    elif direction == "west" and x > 0 and grid[y][x-1] is not None:
                        world.add_door(room, grid[y][x-1], direction)
    
    return world


def decorate_graph(graph: Graph, room_types_file: str, locks_file: str, keys_file: str) -> None:
    room_types = load_json(room_types_file)
    locks_data = load_json(locks_file)
    keys = load_json(keys_file)

    # Assign room types and ensure unique names
    room_name_counts = {}
    for room in graph.rooms:
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
    
    for room in graph.rooms:
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
                random_room = random.choice(list(graph.rooms))
                random_room.add_item(matching_key)
                all_items.remove(matching_key)

def add_biomes(graph: Graph, biomes_file: str, scale_factor: int = 1.5) -> None:
    biomes_data = load_json(biomes_file)
    biome_types = [biome["name"] for biome in biomes_data]

    # Hard-coded grid size
    grid_size = 10  # You can adjust this value as needed

    # Create a larger Voronoi diagram for biomes
    points = np.random.rand(len(biome_types) * 2, 2) * (grid_size * scale_factor)
    vor = Voronoi(points)

    # Assign random biome types to Voronoi regions
    region_biomes = {i: np.random.choice(biome_types) for i in range(len(vor.regions))}

    # Assign biomes to rooms based on closest Voronoi region
    for room in graph.rooms:
        closest_region = None
        min_distance = float('inf')
        room_point = np.array([room.x * scale_factor, room.y * scale_factor])

        for i, point in enumerate(vor.points):
            distance = np.linalg.norm(room_point - point)
            if distance < min_distance:
                min_distance = distance
                closest_region = vor.point_region[i]

        if closest_region is not None and closest_region in region_biomes:
            room.biome = region_biomes[closest_region].capitalize()
        else:
            # Fallback: assign a random biome if the closest region is not found
            room.biome = random.choice(biome_types).capitalize()

        print(f"Room: ({room.x}, {room.y}), Closest Region: {closest_region}, Assigned Biome: {room.biome}")

def generate_world(num_rooms: int, grid_size: int, room_types_file: str, locks_file: str, keys_file: str, biomes_file: str) -> Graph:
    graph = get_voronoi_graph(num_rooms, grid_size * 10)
    add_biomes(graph, biomes_file)
    dynamic_decorate_graph(graph, room_types_file, locks_file, keys_file)
    return graph

def decorate_graph(graph: Graph, room_types_file: str, locks_file: str, keys_file: str) -> None:
    room_types = load_json(room_types_file)
    locks_data = load_json(locks_file)
    keys = load_json(keys_file)

    # Assign room types and ensure unique names
    room_name_counts = {}
    for room in graph.rooms:
        compatible_room_types = [rt for rt in room_types if room.biome.lower() in rt["biomes"]]
        if not compatible_room_types:
            compatible_room_types = room_types  # Fallback to all room types if none match the biome
        
        room_type = random.choice(compatible_room_types)
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
    
    for room in graph.rooms:
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
                random_room = random.choice(list(graph.rooms))
                random_room.add_item(matching_key)
                all_items.remove(matching_key)

def print_map(graph: Graph) -> None:
    map_text = Text()

    try:
        # Calculate grid size based on room positions
        min_x = min(room.x for room in graph.rooms)
        max_x = max(room.x for room in graph.rooms)
        min_y = min(room.y for room in graph.rooms)
        max_y = max(room.y for room in graph.rooms)

        grid_width = max_x - min_x + 1
        grid_height = max_y - min_y + 1

        # Create a grid representation
        grid = [[None for _ in range(grid_width)] for _ in range(grid_height)]
        for room in graph.rooms:
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
    except Exception as e:
        show_error("Error while trying to render grid map", e)

    # Print detailed room information
    map_text.append("Room Details:\n")
    for room in graph.rooms:
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
            if target_room.biome != room.biome:
                door_text.append(f"into the {target_room.biome} to ")
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

    # show_narrative_text(map_text, "World Map (development only)")
