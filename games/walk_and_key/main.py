import random
from utils.gui.display_interface import (
    show_narrative_text,
    get_user_text,
    show_situation,
    start_display,
    stop_display,
    show_error
)

class Room:
    def __init__(self, name):
        self.name = name
        self.doors = {}

    def add_door(self, direction, room):
        self.doors[direction] = room

class Graph:
    def __init__(self):
        self.rooms = {}

    def add_room(self, room):
        self.rooms[room.name] = room

    def add_door(self, room1_name, room2_name, direction):
        room1 = self.rooms[room1_name]
        room2 = self.rooms[room2_name]
        opposite_direction = {
            "north": "south",
            "south": "north",
            "east": "west",
            "west": "east"
        }
        room1.add_door(direction, room2)
        room2.add_door(opposite_direction[direction], room1)

class Player:
    def __init__(self, current_room):
        self.current_room = current_room

def create_world():
    world = Graph()
    rooms = ["Living Room", "Kitchen", "Bedroom", "Bathroom", "Study"]
    for room_name in rooms:
        world.add_room(Room(room_name))

    world.add_door("Living Room", "Kitchen", "north")
    world.add_door("Living Room", "Bedroom", "east")
    world.add_door("Bedroom", "Bathroom", "north")
    world.add_door("Living Room", "Study", "south")

    return world

def main():
    start_display()
    world = create_world()
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
