import random
import toml
from typing import List
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
        situation = f"You are in the {player.current_room.get_size_description()} {player.current_room.name}.\n"
        
        situation += "Your inventory:\n"
        if player.inventory:
            for item in player.inventory:
                situation += f"- {item}\n"
        else:
            situation += "Your inventory is empty.\n"
        
        if player.current_room.items:
            situation += "\nItems in the room:\n"
            for item in player.current_room.items:
                situation += f"- {item}\n"
        else:
            situation += "\nThere are no items in this room.\n"
        
        situation += "\nAvailable options:\n"
        
        # Movement actions
        for direction, door in player.current_room.doors.items():
            target_room = door.room2 if door.room1 == player.current_room else door.room1
            lock_status = f" ({door.get_lock_description()})" if door.is_locked() else ""
            description = f"Go {direction} to the {target_room.name}{lock_status}"
            actions.append(Action(ActionType.MOVE, door, description))
        
        # Pick up actions
        for item in player.current_room.items:
            description = f"Pick up {item['name']}"
            actions.append(Action(ActionType.PICK_UP, item, description))
        
        # Use actions
        for item in player.inventory:
            description = f"Use {item['name']}"
            actions.append(Action(ActionType.USE, item, description))
        
        # Quit action
        actions.append(Action(ActionType.QUIT, None, "Quit"))
        
        # Display actions
        for i, action in enumerate(actions):
            situation += f"{chr(97 + i)}. {action}\n"
        
        show_narrative_text(situation, "Options")

        choice = get_user_text("Enter your choice: ").lower()

        if choice.isalpha() and ord(choice) - 97 < len(actions):
            action = actions[ord(choice) - 97]
            
            if action.action_type == ActionType.QUIT:
                show_narrative_text("Thanks for playing!")
                break
            elif action.action_type == ActionType.PICK_UP:
                player.add_to_inventory(action.target)
                player.current_room.remove_item(action.target)
                show_narrative_text(f"You picked up the {action.target['name']}. {action.target['description']}")
            elif action.action_type == ActionType.USE:
                if "Key" in action.target['name']:
                    key_color = action.target['color']
                    unlocked_doors = []
                    for direction, door in player.current_room.doors.items():
                        if door.is_locked() and door.lock['color'] == key_color:
                            door.unlock()
                            unlocked_doors.append(direction)
                    if unlocked_doors:
                        show_narrative_text(f"You used the {action.target['name']} to unlock the door(s) to the {', '.join(unlocked_doors)}.")
                    else:
                        show_narrative_text(f"There are no {key_color} locked doors in this room.")
                else:
                    show_narrative_text(f"You used the {action.target['name']}, but nothing happened.")
            elif action.action_type == ActionType.MOVE:
                door = action.target
                if door.is_locked():
                    show_narrative_text(door.get_lock_description())
                else:
                    player.current_room = door.room2 if door.room1 == player.current_room else door.room1
                    show_narrative_text(f"You move to the {player.current_room.name}.")
        else:
            show_error("Invalid choice. Please try again.")

    stop_display()

if __name__ == "__main__":
    main()
