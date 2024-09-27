from typing import Dict, List, Optional

from games.walk_and_key.lock import Lock
from games.walk_and_key.room_and_door import Room, Door


class Graph:
    def __init__(self):
        self.rooms: List[Room] = []
        self.starting_room: Optional[Room] = None

    def add_room(self, room: Room) -> None:
        self.rooms.append(room)

    def all_doors(self):
        visited_doors = set()
        for room in self.rooms:
            for door in room.doors.values():
                if door not in visited_doors:
                    visited_doors.add(door)
                    yield door

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

    def get_neighboring_rooms(self, room: Room) -> List[Room]:
        neighboring_rooms = []
        for direction, door in room.doors.items():
            neighboring_room = door.room1 if door.room2 == room else door.room2
            neighboring_rooms.append(neighboring_room)
        return neighboring_rooms

    def get_doors_for_room_bidirectional(self, room: Room) -> List[Door]:
        return list(room.doors.values())

    def get_door_between(self, room1: Room, room2: Room) -> Optional[Door]:
        for door in room1.doors.values():
            if door.room1 == room2 or door.room2 == room2:
                return door
        return None

    def remove_locked_doors_with_no_key(self):
        for room in self.rooms:
            room.doors = {direction: door for direction, door in room.doors.items() if not door.is_locked_with_no_key()}
