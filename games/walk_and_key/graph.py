from typing import Dict, List, Optional

from games.walk_and_key.lock import Lock
from games.walk_and_key.room_and_door import Room, Door


class Graph:
    def __init__(self):
        self.rooms: List[Room] = []
        self.doors: List[Door] = []

    def add_room(self, room: Room) -> None:
        self.rooms.append(room)

    def add_door(self, room1: Room, room2: Room, direction: str, lock: Optional[Lock] = None) -> None:
        opposite_direction = {
            "north": "south",
            "south": "north",
            "east": "west",
            "west": "east"
        }
        door = Door(room1, room2, direction, lock)
        room1.add_door(direction, door)
        room2.add_door(opposite_direction[direction], door)
        self.doors.append(door)

    def get_neighboring_rooms(self, room: Room) -> List[Room]:
        neighboring_rooms = []
        for door in self.doors:
            if door.room1 == room:
                neighboring_rooms.append(door.room2)
            elif door.room2 == room:
                neighboring_rooms.append(door.room1)
        return neighboring_rooms

    def get_doors_for_room_bidirectional(self, room: Room) -> List[Door]:
        return [door for door in self.doors if door.room1 == room or door.room2 == room]
