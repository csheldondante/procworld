from typing import List, Dict, Set, Optional, Tuple
import random

from games.walk_and_key.item import Item
from games.walk_and_key.lockandkeyplayer import LockAndKeyPlayer
from games.walk_and_key.lock import Lock
from games.walk_and_key.room_and_door import Room, Door
from games.walk_and_key.utils.json import load_json
from games.walk_and_key.graph import Graph
from games.walk_and_key.item import Item
from utils.gui.display_interface import show_error


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
    player_path, log = simulate_player_movement(graph, locks, keys)

    # print(f"\n\nPlayer path!\n")
    # print("\n".join(log))

    # Add remaining keys and locks to create alternative paths
    # TODO This is a good idea but needs to be handled with care
    # add_alternative_paths(graph, locks, keys)

    # Add miscellaneous items to rooms
    add_misc_items(graph)

    # Reset annotations
    for room in graph.rooms:
        room.visited = False

    # Delete all doors which are locked with no key
    for room in graph.rooms:
        room.doors = {d: door for d, door in room.doors.items() if not door.is_locked_with_no_key()}


def initialize_rooms(graph: Graph, room_types: List[Dict]) -> None:
    room_name_counts: Dict[str, int] = {}
    for room in graph.rooms:
        compatible_room_types = [rt for rt in room_types if room.biome.lower() in rt.get("biomes", [])]
        if not compatible_room_types:
            show_error(f"No room types found for biome {room.biome}")
            compatible_room_types = room_types  # Fallback to all room types if none match the biome
        room_type = random.choice(compatible_room_types)
        room.room_type = room_type["name"]
        room.adjectives = room_type["adjectives"][:3]
        room.size = room_type["size"]
        room.description = room_type["description"]
        room.name = generate_unique_name(room, room_name_counts)
        room.visited = False
        room.items = []


def simulate_player_movement(graph: Graph, locks: List[Lock], keys: List[Item]) -> Tuple[List[Room], List[str]]:
    start_room = random.choice(graph.rooms)
    graph.starting_room = start_room
    current_room = start_room
    player_path = [current_room]
    player = LockAndKeyPlayer(graph.starting_room)
    visited_rooms: Set[Room] = set()

    # Initialize the log
    log: List[str] = [f"Player starts in {current_room.name}"]

    # Start with all doors locked with no key
    for door in graph.all_doors():
        door.set_locked_with_no_key()

    while len(visited_rooms) < len(graph.rooms):
        # print(f"Current room: {current_room.name}")
        # print(f"Visited rooms: {len(visited_rooms)}/{len(graph.rooms)}")
        current_room.visited = True
        visited_rooms.add(current_room)

        # Check neighboring rooms and potentially create locks and keys
        for neighbor in graph.get_neighboring_rooms(current_room):
            connecting_door = graph.get_door_between(current_room, neighbor)
            # print(f"Checking door to {neighbor.name}: {'Locked' if connecting_door.is_locked() else 'Unlocked'}")
            if connecting_door.is_locked_with_no_key():
                if random.random() < 0.7:  # 70% chance to create a lock and key
                    new_lock = create_lock(locks)
                    if new_lock:
                        connecting_door.set_lock(new_lock)
                        new_key = create_key(keys, new_lock.color)
                        if new_key:
                            current_room.items.append(new_key)
                            player.inventory.append(new_key)
                            log.append(f"Player finds a {new_key.name} in {current_room.name}")
                            # print(f"Created lock and key for door to {neighbor.name}")
                        else:
                            log.append(f"Player discovers a locked door to {neighbor.name} but can't find a key")
                            # print(f"Created lock but no key available for door to {neighbor.name}")
                    else:
                        log.append(f"Player discovers a locked door to {neighbor.name}")
                        # print(f"No lock available for door to {neighbor.name}")
                else:
                    log.append(f"Player discovers a locked door to {neighbor.name}")
                    # print(f"Decided not to create lock for door to {neighbor.name}")

        # Move to next room
        next_room = choose_next_room(graph, current_room, visited_rooms)
        if next_room:
            connecting_door = graph.get_door_between(current_room, next_room)
            if connecting_door.can_player_unlock(player):
                player_path.append(next_room)
                log.append(f"Player moves to {next_room.name}")
                current_room = next_room
            else:
                log.append(f"Player can't move to {next_room.name} due to a locked door")
        else:
            # Backtrack if stuck
            player_path.pop()
            if player_path:
                current_room = player_path[-1]
                log.append(f"Player backtracks to {current_room.name}")
            else:
                log.append("Player has explored all accessible rooms")
                break  # Exit the loop if we've backtracked to the start

    return player_path, log


def create_lock(locks: List[Lock]) -> Optional[Lock]:
    lock = random.choice(locks)
    return lock


def create_key(keys: List[Item], color: str) -> Optional[Item]:
    matching_keys = [key for key in keys if key.color == color]
    if matching_keys:
        key = random.choice(matching_keys)
        keys.remove(key)
        return key
    return None


def choose_next_room(graph: Graph, current_room: Room, visited_rooms: Set[Room]) -> Optional[Room]:
    unvisited_neighbors = [
        room for room in graph.get_neighboring_rooms(current_room)
        if room not in visited_rooms
    ]
    return random.choice(unvisited_neighbors) if unvisited_neighbors else None


# def add_alternative_paths(graph: Graph, locks: List[Lock], keys: List[Item]) -> None:
#     for door in graph.doors:
#         if not door.lock and random.random() < 0.2:  # 20% chance to add a lock
#             new_lock = create_lock(locks)
#             if new_lock:
#                 door.lock = new_lock
#
#                 # Place the corresponding key in a random room
#                 new_key = create_key(keys, new_lock.color)
#                 if new_key:
#                     random_room = random.choice(graph.rooms)
#                     random_room.items.append(new_key)


def add_misc_items(graph: Graph) -> None:
    misc_items = load_json("data/items.json")
    items = [Item(item["name"], item["color"], item["adjectives"], item["description"]) for item in misc_items]

    for room in graph.rooms:
        num_items = random.choices([0, 1, 2], weights=[0.3, 0.5, 0.2])[0]  # 30% chance for 0, 50% for 1, 20% for 2
        for _ in range(num_items):
            if items:
                item = random.choice(items)
                room.items.append(item)
                items.remove(item)
            else:
                # If we run out of unique items, create copies of existing ones
                original_item = random.choice(misc_items)
                new_item = Item(original_item["name"], original_item["color"], original_item["adjectives"], original_item["description"])
                room.items.append(new_item)


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
