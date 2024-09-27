import random
from utils.gui.display_interface import (
    show_narrative_text,
    get_user_text,
    show_situation,
    start_display,
    stop_display,
    show_error
)
from games.walk_and_key.world import Room, Graph, Door, generate_random_graph


class Player:
    def __init__(self, current_room):
        self.current_room = current_room
        self.inventory = []

    def add_to_inventory(self, item):
        self.inventory.append(item)

    def remove_from_inventory(self, item):
        self.inventory.remove(item)


def main():
    start_display()
    world = generate_random_graph(10)
    player = Player(random.choice(list(world.rooms.values())))

    show_narrative_text("Welcome to the Simple Text RPG!", "Introduction")
    while True:
        options = list(player.current_room.doors.items())
        situation = f"You are in the {player.current_room.name}.\n"
        
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
        for i, (direction, door) in enumerate(options):
            target_room = door.room2 if door.room1 == player.current_room else door.room1
            lock_status = " (Locked)" if door.is_locked else ""
            situation += f"{chr(97 + i)}. Go {direction} to the {target_room.name}{lock_status}\n"
        
        for j, item in enumerate(player.current_room.items):
            situation += f"{chr(97 + len(options) + j)}. Pick up {item}\n"
            options.append(("pick up", item))
        
        for k, item in enumerate(player.inventory):
            situation += f"{chr(97 + len(options) + k)}. Use {item}\n"
            options.append(("use", item))
        
        situation += f"{chr(97 + len(options))}. Quit"
        show_narrative_text(situation, "Options")

        choice = get_user_text("Enter your choice: ").lower()

        if choice == chr(97 + len(options)):
            show_narrative_text("Thanks for playing!")
            break
        elif choice.isalpha() and ord(choice) - 97 < len(options):
            action, item_or_door = options[ord(choice) - 97]
            if action == "pick up":
                player.add_to_inventory(item_or_door)
                player.current_room.remove_item(item_or_door)
                show_narrative_text(f"You picked up the {item_or_door}.")
            elif action == "use":
                if "Key" in item_or_door:
                    key_color = item_or_door.split()[0].lower()
                    unlocked_doors = []
                    for direction, door in player.current_room.doors.items():
                        if door.lock_color == key_color:
                            door.lock_color = None
                            unlocked_doors.append(direction)
                    if unlocked_doors:
                        player.remove_from_inventory(item_or_door)
                        show_narrative_text(f"You used the {item_or_door} to unlock the door(s) to the {', '.join(unlocked_doors)}.")
                    else:
                        show_narrative_text(f"There are no {key_color} locked doors in this room.")
                else:
                    show_narrative_text(f"You used the {item_or_door}, but nothing happened.")
            elif isinstance(item_or_door, Door):
                if item_or_door.lock_color:
                    show_narrative_text(f"The door to the {action} is locked with a {item_or_door.lock_color} lock. You need to find a {item_or_door.lock_color} key.")
                else:
                    player.current_room = item_or_door.room2 if item_or_door.room1 == player.current_room else item_or_door.room1
                    show_narrative_text(f"You move {action} to the {player.current_room.name}.")
        else:
            show_error("Invalid choice. Please try again.")

    stop_display()

if __name__ == "__main__":
    main()
