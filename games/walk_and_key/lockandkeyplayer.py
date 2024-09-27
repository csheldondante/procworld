from typing import Set, List
from games.walk_and_key.item import Item
from games.walk_and_key.room_and_door import Room


class LockAndKeyPlayer:
    def __init__(self, current_room: Room):
        self.current_room: Room = current_room
        self.inventory: List[Item] = []

    def add_to_inventory(self, item: Item) -> None:
        self.inventory.append(item)

    def remove_from_inventory(self, item: Item) -> None:
        self.inventory.remove(item)

    def add_item(self, item: Item):
        self.inventory.append(item)

    def remove_item(self, item: Item):
        self.inventory.remove(item)
