import random
from utils.gui.display_interface import (
    show_narrative_text,
    get_user_text,
    show_situation,
    start_display,
    stop_display,
    show_error
)
from games.walk_and_key.world import Room, Graph, generate_random_graph


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
    show_narrative_text(f"You are in the {player.current_room.name}.", "Location")

    while True:
        options = list(player.current_room.doors.items())
        situation = f"You are in the {player.current_room.name}.\n"
        
        if player.current_room.items:
            situation += "Items in the room:\n"
            for item in player.current_room.items:
                situation += f"- {item}\n"
        else:
            situation += "There are no items in this room.\n"
        
        situation += "\nAvailable options:\n"
        for i, (direction, door) in enumerate(options):
            target_room = door.room2 if door.room1 == player.current_room else door.room1
            lock_status = " (Locked)" if door.is_locked else ""
            situation += f"{chr(97 + i)}. Go {direction} to the {target_room.name}{lock_status}\n"
        
        if player.current_room.items:
            situation += f"{chr(97 + len(options))}. Pick up an item\n"
            options.append(("pick up", None))
        
        if player.inventory:
            situation += f"{chr(97 + len(options))}. Use an item from inventory\n"
            options.append(("use item", None))
        
        situation += f"{chr(97 + len(options))}. Quit"
        show_narrative_text(situation, "Options")

        choice = get_user_text("Enter your choice: ").lower()

        if choice == chr(97 + len(options)):
            show_narrative_text("Thanks for playing!")
            break
        elif choice.isalpha() and ord(choice) - 97 < len(options):
            action, door = options[ord(choice) - 97]
            if action == "pick up":
                item_to_pick = get_user_text("Which item do you want to pick up? ").capitalize()
                if item_to_pick in player.current_room.items:
                    player.add_to_inventory(item_to_pick)
                    player.current_room.remove_item(item_to_pick)
                    show_narrative_text(f"You picked up the {item_to_pick}.")
                else:
                    show_error("That item is not in the room.")
            elif action == "use item":
                item_to_use = get_user_text("Which item do you want to use? ").capitalize()
                if item_to_use in player.inventory:
                    if item_to_use == "Key":
                        for direction, door in player.current_room.doors.items():
                            if door.is_locked:
                                door.is_locked = False
                                player.remove_from_inventory("Key")
                                show_narrative_text(f"You unlocked the door to the {direction}.")
                                break
                        else:
                            show_narrative_text("There are no locked doors in this room.")
                    else:
                        show_narrative_text(f"You used the {item_to_use}, but nothing happened.")
                else:
                    show_error("You don't have that item in your inventory.")
            elif door:
                if door.is_locked:
                    show_narrative_text(f"The door to the {action} is locked. You need to find a key.")
                else:
                    player.current_room = door.room2 if door.room1 == player.current_room else door.room1
                    show_narrative_text(f"You move {action} to the {player.current_room.name}.")
        else:
            show_error("Invalid choice. Please try again.")

    stop_display()

if __name__ == "__main__":
    main()
