from typing import Set
from games.walk_and_key.item import Item

class Player:
    def __init__(self):
        self.inventory: Set[Item] = set()

    def add_item(self, item: Item):
        self.inventory.add(item)

    def remove_item(self, item: Item):
        self.inventory.remove(item)
