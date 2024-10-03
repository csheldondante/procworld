import random
import toml
from typing import List, Dict
from rich import print
from rich.text import Text
import string
from games.walk_and_key.item import Item
from games.walk_and_key.lockandkeyplayer import LockAndKeyPlayer
from utils.gui.display_interface import (
    show_narrative_text,
    get_user_text,
    show_situation,
    start_display,
    stop_display,
    show_error
)
from games.walk_and_key.world import generate_world, print_map
from games.walk_and_key.graph import Graph
from games.walk_and_key.room_and_door import Room, Door
from games.walk_and_key.action import Action, ActionType
from rich.text import Text




def pickup_item(player: LockAndKeyPlayer, item: Item) -> Text:
    player.add_to_inventory(item)
    player.current_room.remove_item(item)
    message = Text("You picked up the ")
    message.append(item.get_name())
    message.append(". ")
    message.append(item.description)
    return message


def load_config() -> Dict:
    return toml.load("games/walk_and_key/config.toml")


def initialize_game(config: Dict) -> tuple[Graph, LockAndKeyPlayer]:
    world = generate_world(
        config["game"]["num_rooms"],
        config["game"]["grid_size"],
        config["files"]["room_types"],
        config["files"]["locks"],
        config["files"]["keys"],
        config["files"]["biomes"],
    )
    starting_room = world.starting_room
    starting_room.visited = True
    player = LockAndKeyPlayer(starting_room)
    return world, player


def autopickup_items(player: LockAndKeyPlayer, config: Dict) -> None:
    if config["game"]["autopickup"] and player.current_room.items:
        for item in player.current_room.items[:]:  # Create a copy of the list to iterate over
            message = pickup_item(player, item)
            show_narrative_text(message, "Item Pickup")


def describe_situation(player: LockAndKeyPlayer) -> Text:
    situation = player.current_room.get_full_description()
    
    situation.append("\nYour inventory:\n")
    if player.inventory:
        for item in player.inventory:
            situation.append("- ")
            situation.append(item.get_name())
            situation.append("\n")
    else:
        situation.append("Your inventory is empty.\n")
    
    situation.append("\nAvailable options:\n")
    return situation


def get_available_actions(player: LockAndKeyPlayer, world: Graph) -> List[Action]:
    actions = []
    
    # Movement actions
    for direction, door in player.current_room.doors.items():
        target_room = door.room2 if door.room1 == player.current_room else door.room1
        description = Text()
        description.append(f"Go {direction}")
        if target_room.biome != player.current_room.biome:
            description.append(f" into the ")
            description.append(target_room.biome, style="bold")
        description.append(" to the ")
        description.append(target_room.get_name())
        if target_room.visited:
            description.append(" (visited)")
        if door.is_locked():
            description.append(" (")
            description.append(door.get_lock_description_short())
            description.append(")")
        actions.append(Action(ActionType.MOVE, door, description))
    
    # Pick up actions
    for item in player.current_room.items:
        description = Text("Pick up ")
        description.append(item.get_name())
        actions.append(Action(ActionType.PICK_UP, item, description))
    
    # Use actions
    for item in player.inventory:
        description = Text("Use ")
        description.append(item.get_name())
        actions.append(Action(ActionType.USE, item, description))
    
    # Quit action
    actions.append(Action(ActionType.QUIT, None, Text("Quit")))
    
    return actions


def display_actions(situation: Text, actions: List[Action]) -> None:
    alphabet = string.ascii_lowercase
    for i, action in enumerate(actions):
        if i < len(alphabet):
            situation.append(f"{alphabet[i]}. ")
            if isinstance(action.description, Text):
                situation.append(action.description)
            else:
                situation.append(action)
            situation.append("\n")
        else:
            break
    show_narrative_text(situation, "Options")


def handle_action(action: Action, player: LockAndKeyPlayer, config: Dict) -> bool:
    if action.action_type == ActionType.QUIT:
        show_narrative_text("Thanks for playing!")
        return False
    elif action.action_type == ActionType.PICK_UP:
        message = pickup_item(player, action.target)
        show_narrative_text(message, "Item Pickup")
    elif action.action_type == ActionType.USE:
        if "Key" in action.target.name:
            use_key(player, action.target)
        else:
            message = Text()
            message.append("You used the ")
            message.append(action.target.get_name())
            message.append(", but nothing happened.")
            show_narrative_text(message)
    elif action.action_type == ActionType.MOVE:
        move_player(player, action.target, config)
    return True


def use_key(player: LockAndKeyPlayer, key: Item) -> None:
    key_color = key.color
    unlocked_doors = []
    for direction, door in player.current_room.doors.items():
        if door.is_locked() and door.lock.color == key_color:
            door.unlock()
            unlocked_doors.append(direction)
    if unlocked_doors:
        message = Text("You used the ")
        message.append(key.get_name())
        message.append(f" to unlock the door(s) to the {', '.join(unlocked_doors)}.")
        show_narrative_text(message)
        # Key is not removed from inventory
    else:
        message = Text("There are no ")
        message.append(Text(key_color, style=f"bold {key_color}"))
        message.append(" locked doors in this room.")
        show_narrative_text(message, "Action")


def move_player(player: LockAndKeyPlayer, door: Door, config: Dict) -> None:
    if door.is_locked():
        show_narrative_text(door.get_lock_description(), "Locked door")
    else:
        player.current_room = door.room2 if door.room1 == player.current_room else door.room1
        player.current_room.visited = True
        message = Text()
        message.append("You move to the ")
        message.append(player.current_room.get_name())
        message.append(".")
        show_narrative_text(message)
        autopickup_items(player, config)


def main() -> None:
    start_display()
    
    config = load_config()
    world, player = initialize_game(config)

    print_map(world)  # Print the map for development purposes

    show_narrative_text("Welcome to the Lock and Key RPG!", "Introduction")
    
    autopickup_items(player, config)  # Autopickup items in the starting room
    
    while True:
        situation = describe_situation(player)
        actions = get_available_actions(player, world)
        display_actions(situation, actions)

        choice = get_user_text("Enter your choice: ").lower()
        alphabet = string.ascii_lowercase

        if choice in alphabet[:len(actions)]:
            action = actions[alphabet.index(choice)]
            if not handle_action(action, player, config):
                break
        else:
            show_error("Invalid choice. Please try again.")

    stop_display()

if __name__ == "__main__":
    main()
