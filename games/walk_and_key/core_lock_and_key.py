from typing import List, Dict, Set, Optional
import random

from games.walk_and_key.item import Item
from games.walk_and_key.lock import Lock
from games.walk_and_key.room_and_door import Room, Door
from games.walk_and_key.utils.json import load_json
from games.walk_and_key.graph import Graph


def dynamic_decorate_graph(graph: Graph, room_types_file: str, locks_file: str, keys_file: str) -> None:
    room_types = load_json(room_types_file)
    locks_data = load_json(locks_file)
    keys_data = load_json(keys_file)

    # Initialize rooms with basic information
    initialize_rooms(graph, room_types)

    # Create Lock and Key objects
    locks = [Lock(lock["name"], lock["color"], lock["adjectives"], lock["description"]) for lock in locks_data]
    keys = [Item(key["name"], key["color"], key["adjectives"], key["description"]) for key in keys_data]

    # Simulate player movement and decorate the graph
    player_path = simulate_player_movement(graph, locks, keys)

    # Add remaining keys and locks to create alternative paths
    add_alternative_paths(graph, locks, keys)

    # Add miscellaneous items to rooms
    add_misc_items(graph)


def initialize_rooms(graph: Graph, room_types: List[Dict]) -> None:
    room_name_counts: Dict[str, int] = {}
    for room in graph.rooms:
        room_type = random.choice(room_types)
        room.room_type = room_type["name"]
        room.adjectives = room_type["adjectives"][:3]
        room.size = room_type["size"]
        room.description = room_type["description"]
        room.name = generate_unique_name(room, room_name_counts)
        room.visited = False
        room.items = []


def simulate_player_movement(graph: Graph, locks: List[Lock], keys: List[Item]) -> List[Room]:
    start_room = random.choice(graph.rooms)
    current_room = start_room
    player_path = [current_room]
    player_keys: Set[Item] = set()
    visited_rooms: Set[Room] = set()
    known_locked_doors: Set[Lock] = set()

    while len(visited_rooms) < len(graph.rooms):
        current_room.visited = True
        visited_rooms.add(current_room)

        # Update known locked doors
        for door in graph.get_doors_for_room_bidirectional(current_room):
            if door.lock and door.lock not in known_locked_doors:
                known_locked_doors.add(door.lock)

        # Place a key if needed
        if not player_keys and known_locked_doors:
            place_key(current_room, keys, list(known_locked_doors)[0])
            if keys:
                player_keys.add(keys[-1])

        # Try to use a key
        for door in graph.get_doors_for_room_bidirectional(current_room):
            if door.lock and door.lock.color in [key.color for key in player_keys]:
                door.lock = None
                player_keys.remove(next(key for key in player_keys if key.color == door.lock.color))
                break

        # Move to next room
        next_room = choose_next_room(graph, current_room, visited_rooms)
        if next_room:
            player_path.append(next_room)
            current_room = next_room
        else:
            # Backtrack if stuck
            player_path.pop()
            if player_path:
                current_room = player_path[-1]
            else:
                break  # Exit the loop if we've backtracked to the start

    return player_path


def choose_next_room(graph: Graph, current_room: Room, visited_rooms: Set[Room]) -> Optional[Room]:
    unvisited_neighbors = [
        room for room in graph.get_neighboring_rooms(current_room)
        if room not in visited_rooms
    ]
    return random.choice(unvisited_neighbors) if unvisited_neighbors else None


def place_key(room: Room, keys: List[Item], lock: Lock) -> None:
    matching_key = next((key for key in keys if key.color == lock.color), None)
    if matching_key:
        room.items.append(matching_key)
        keys.remove(matching_key)


def add_alternative_paths(graph: Graph, locks: List[Lock], keys: List[Item]) -> None:
    for door in graph.doors:
        if not door.lock and random.random() < 0.2:  # 20% chance to add a lock
            if locks:
                lock = random.choice(locks)
                door.lock = lock
                locks.remove(lock)

                # Place the corresponding key in a random room
                if keys:
                    matching_key = next((key for key in keys if key.color == lock.color), None)
                    if matching_key:
                        random_room = random.choice(list(graph.rooms))
                        random_room.items.append(matching_key)
                        keys.remove(matching_key)


def add_misc_items(graph: Graph) -> None:
    misc_items = [
        Item("Mysterious Object", "gray", ["intriguing", "odd", "peculiar"],
             "An object of unknown origin and purpose."),
        # Add more miscellaneous items here
    ]

    for room in graph.rooms:
        if random.random() < 0.3:  # 30% chance to add a misc item
            if misc_items:
                item = random.choice(misc_items)
                room.items.append(item)
                misc_items.remove(item)


def generate_unique_name(room: Room, room_name_counts: Dict[str, int]) -> str:
    base_name = f"{room.room_type.replace('_', ' ').title()}"
    if base_name in room_name_counts:
        room_name_counts[base_name] += 1
        count = room_name_counts[base_name]
        if count <= len(room.adjectives):
            return f"{room.adjectives[count - 1].capitalize()} {base_name}"
        else:
            return f"{base_name} {count}"
    else:
        room_name_counts[base_name] = 1
        return base_name
