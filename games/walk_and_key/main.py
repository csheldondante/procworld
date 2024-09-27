import random
import toml
from typing import List, Dict
from rich import print
from rich.text import Text
import string
from games.walk_and_key.item import Item
from utils.gui.display_interface import (
    show_narrative_text,
    get_user_text,
    show_situation,
    start_display,
    stop_display,
    show_error
)
from games.walk_and_key.world import Room, Graph, Door, generate_world, print_map
from games.walk_and_key.action import Action, ActionType


class Player:
    def __init__(self, current_room: Room):
        self.current_room: Room = current_room
        self.inventory: List[Item] = []

    def add_to_inventory(self, item: Item) -> None:
        self.inventory.append(item)

    def remove_from_inventory(self, item: Item) -> None:
        self.inventory.remove(item)


def load_config() -> Dict:
    return toml.load("games/walk_and_key/config.toml")


def initialize_game(config: Dict) -> tuple[Graph, Player]:
    world = generate_world(
        config["game"]["num_rooms"],
        config["files"]["room_types"],
        config["files"]["locks"],
        config["files"]["keys"]
    )
    player = Player(random.choice(list(world.rooms.values())))
    return world, player


def describe_situation(player: Player) -> Text:
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


def get_available_actions(player: Player) -> List[Action]:
    actions = []
    
    # Movement actions
    for direction, door in player.current_room.doors.items():
        target_room = door.room2 if door.room1 == player.current_room else door.room1
        description = Text()
        description.append(f"Go {direction} to the ")
        description.append(target_room.get_name())
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


def handle_action(action: Action, player: Player) -> bool:
    if action.action_type == ActionType.QUIT:
        show_narrative_text("Thanks for playing!")
        return False
    elif action.action_type == ActionType.PICK_UP:
        player.add_to_inventory(action.target)
        player.current_room.remove_item(action.target)
        message = Text("You picked up the ")
        message.append(action.target.get_name())
        message.append(". ")
        message.append(action.target.description)
        show_narrative_text(message)
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
        move_player(player, action.target)
    return True


def use_key(player: Player, key: Item) -> None:
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
    else:
        message = Text("There are no ")
        message.append(Text(key_color, style=f"bold {key_color}"))
        message.append(" locked doors in this room.")
        show_narrative_text(message, "Action")


def move_player(player: Player, door: Door) -> None:
    if door.is_locked():
        show_narrative_text(door.get_lock_description(), "Locked door")
    else:
        player.current_room = door.room2 if door.room1 == player.current_room else door.room1
        message = Text()
        message.append("You move to the ")
        message.append(player.current_room.get_name())
        message.append(".")
        show_narrative_text(message)


def main() -> None:
    start_display()
    
    config = load_config()
    world, player = initialize_game(config)

    print_map(world)  # Print the map for development purposes

    show_narrative_text("Welcome to the Lock and Key RPG!", "Introduction")
    
    while True:
        situation = describe_situation(player)
        actions = get_available_actions(player)
        display_actions(situation, actions)

        choice = get_user_text("Enter your choice: ").lower()
        alphabet = string.ascii_lowercase

        if choice in alphabet[:len(actions)]:
            action = actions[alphabet.index(choice)]
            if not handle_action(action, player):
                break
        else:
            show_error("Invalid choice. Please try again.")

    stop_display()

if __name__ == "__main__":
    main()
