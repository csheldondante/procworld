import random

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
    world = create_world()
    player = Player(random.choice(list(world.rooms.values())))

    print("Welcome to the Simple Text RPG!")
    print(f"You find yourself in the {player.current_room.name}.")

    while True:
        print("\nWhat would you like to do?")
        print("Available doors:")
        for direction, room in player.current_room.doors.items():
            print(f"- Go {direction} to the {room.name}")
        print("- Quit")

        choice = input("Enter your choice: ").lower()

        if choice == "quit":
            print("Thanks for playing!")
            break
        elif choice in player.current_room.doors:
            player.current_room = player.current_room.doors[choice]
            print(f"You move to the {player.current_room.name}.")
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
