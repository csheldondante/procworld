import random
import toml
from typing import List
from rich import print
from rich.text import Text
import string
from utils.gui.display_interface import (
    show_narrative_text,
    get_user_text,
    show_situation,
    start_display,
    stop_display,
    show_error
)
from games.walk_and_key.world import Room, Graph, Door, generate_world
from games.walk_and_key.action import Action, ActionType


class Player:
    def __init__(self, current_room: Room):
        self.current_room: Room = current_room
        self.inventory: List[str] = []

    def add_to_inventory(self, item: str) -> None:
        self.inventory.append(item)

    def remove_from_inventory(self, item: str) -> None:
        self.inventory.remove(item)


def main() -> None:
    start_display()
    
    # Load configuration
    config = toml.load("games/walk_and_key/config.toml")
    
    world = generate_world(
        config["game"]["num_rooms"],
        config["files"]["room_types"],
        config["files"]["locks"],
        config["files"]["keys"]
    )
    player = Player(random.choice(list(world.rooms.values())))

    show_narrative_text("Welcome to the Lock and Key RPG!", "Introduction")
    while True:
        actions = []
        situation = Text()
        situation.append(f"You are in the {player.current_room.get_size_description()} ")
        situation.append(player.current_room.name, style="bold")
        situation.append(".\n\n")
        
        situation.append("Your inventory:\n")
        if player.inventory:
            for item in player.inventory:
                situation.append(f"- ")
                situation.append(item['name'], style=f"bold {item['color']}")
                situation.append("\n")
        else:
            situation.append("Your inventory is empty.\n")
        
        if player.current_room.items:
            situation.append("\nItems in the room:\n")
            for item in player.current_room.items:
                situation.append(f"- ")
                situation.append(item['name'], style=f"bold {item['color']}")
                situation.append("\n")
        else:
            situation.append("\nThere are no items in this room.\n")
        
        situation.append("\nAvailable options:\n")
        
        # Movement actions
        for direction, door in player.current_room.doors.items():
            target_room = door.room2 if door.room1 == player.current_room else door.room1
            lock_status = f" ({door.get_lock_description()})" if door.is_locked() else ""
            description = Text()
            description.append(f"Go {direction} to the ")
            description.append(target_room.name, style="bold")
            description.append(lock_status)
            actions.append(Action(ActionType.MOVE, door, str(description)))
        
        # Pick up actions
        for item in player.current_room.items:
            description = Text()
            description.append("Pick up ")
            description.append(item['name'], style=f"bold {item['color']}")
            actions.append(Action(ActionType.PICK_UP, item, str(description)))
        
        # Use actions
        for item in player.inventory:
            description = Text()
            description.append("Use ")
            description.append(item['name'], style=f"bold {item['color']}")
            actions.append(Action(ActionType.USE, item, str(description)))
        
        # Quit action
        actions.append(Action(ActionType.QUIT, None, "Quit"))
        
        # Display actions
        alphabet = string.ascii_lowercase
        for i, action in enumerate(actions):
            if i < len(alphabet):
                situation.append(f"{alphabet[i]}. {action}\n")
            else:
                break

        print(situation)
        show_narrative_text(str(situation), "Options")

        choice = get_user_text("Enter your choice: ").lower()

        if choice in alphabet[:len(actions)]:
            action = actions[alphabet.index(choice)]
            
            if action.action_type == ActionType.QUIT:
                show_narrative_text("Thanks for playing!")
                break
            elif action.action_type == ActionType.PICK_UP:
                player.add_to_inventory(action.target)
                player.current_room.remove_item(action.target)
                message = Text()
                message.append("You picked up the ")
                message.append(action.target['name'], style=f"bold {action.target['color']}")
                message.append(f". {action.target['description']}")
                show_narrative_text(str(message))
            elif action.action_type == ActionType.USE:
                if "Key" in action.target['name']:
                    key_color = action.target['color']
                    unlocked_doors = []
                    for direction, door in player.current_room.doors.items():
                        if door.is_locked() and door.lock['color'] == key_color:
                            door.unlock()
                            unlocked_doors.append(direction)
                    if unlocked_doors:
                        message = Text()
                        message.append("You used the ")
                        message.append(action.target['name'], style=f"bold {action.target['color']}")
                        message.append(f" to unlock the door(s) to the {', '.join(unlocked_doors)}.")
                        show_narrative_text(str(message))
                    else:
                        show_narrative_text(f"There are no {key_color} locked doors in this room.")
                else:
                    message = Text()
                    message.append("You used the ")
                    message.append(action.target['name'], style=f"bold {action.target['color']}")
                    message.append(", but nothing happened.")
                    show_narrative_text(str(message))
            elif action.action_type == ActionType.MOVE:
                door = action.target
                if door.is_locked():
                    show_narrative_text(door.get_lock_description())
                else:
                    player.current_room = door.room2 if door.room1 == player.current_room else door.room1
                    message = Text()
                    message.append("You move to the ")
                    message.append(player.current_room.name, style="bold")
                    message.append(".")
                    show_narrative_text(str(message))
        else:
            show_error("Invalid choice. Please try again.")

    stop_display()

if __name__ == "__main__":
    main()
