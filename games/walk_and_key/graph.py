from typing import Dict, List, Optional

from games.walk_and_key.lock import Lock
from games.walk_and_key.room_and_door import Room, Door


class Graph:
    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.doors: List[Door] = []

    def add_room(self, room: Room) -> None:
        self.rooms[room.name] = room

    def add_door(self, room1_name: str, room2_name: str, direction: str, lock: Optional[Lock] = None) -> None:
        room1 = self.rooms[room1_name]
        room2 = self.rooms[room2_name]
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

    def get_neighboring_rooms(self, room_name: str) -> List[Room]:
        neighboring_rooms = []
        for door in self.doors:
            if door.room1.name == room_name:
                neighboring_rooms.append(door.room2)
            elif door.room2.name == room_name:
                neighboring_rooms.append(door.room1)
        return neighboring_rooms

    def get_doors_for_room(self, room_name: str) -> List[Door]:
        return [door for door in self.doors if door.room1.name == room_name or door.room2.name == room_name]
