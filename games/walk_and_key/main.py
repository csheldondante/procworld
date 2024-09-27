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


def main():
    start_display()
    world = generate_random_graph(10)
    player = Player(random.choice(list(world.rooms.values())))

    show_narrative_text("Welcome to the Simple Text RPG!", "Introduction")
    show_narrative_text(f"You are in the {player.current_room.name}.", "Location")

    while True:
        options = list(player.current_room.doors.items())
        situation = "Available options:\n"
        for i, (direction, room) in enumerate(options):
            situation += f"{chr(97 + i)}. Go {direction} to the {room.name}\n"
        situation += f"{chr(97 + len(options))}. Quit"
        show_narrative_text(situation, "Options")

        choice = get_user_text("Enter your choice: ").lower()

        if choice == chr(97 + len(options)):
            show_narrative_text("Thanks for playing!")
            break
        elif choice.isalpha() and ord(choice) - 97 < len(options):
            direction, room = options[ord(choice) - 97]
            player.current_room = room
            show_narrative_text(f"You move {direction} to the {player.current_room.name}.")
        else:
            show_error("Invalid choice. Please try again.")

    stop_display()

if __name__ == "__main__":
    main()
