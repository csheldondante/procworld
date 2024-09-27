from typing import List, Dict
from rich.text import Text
from games.walk_and_key.door import Door
from games.walk_and_key.item import Item

class Room:
    def __init__(self, name: str, room_type: str, size: int, adjectives: List[str], description: str, x: int = -1, y: int = -1):
        self.name: str = name
        self.room_type: str = room_type
        self.size: int = size
        self.adjectives: List[str] = adjectives
        self.description: str = description
        self.doors: Dict[str, Door] = {}
        self.items: List[Item] = []
        self.x: int = x
        self.y: int = y

    def add_door(self, direction: str, door: Door) -> None:
        self.doors[direction] = door

    def add_item(self, item: Item) -> None:
        self.items.append(item)

    def remove_item(self, item: Item) -> None:
        self.items.remove(item)

    def get_name(self) -> Text:
        return Text(self.name, style="bold")

    def get_size_description(self) -> Text:
        if self.size <= 2:
            return Text("tiny")
        elif self.size <= 4:
            return Text("small")
        elif self.size <= 6:
            return Text("medium-sized")
        elif self.size <= 8:
            return Text("large")
        else:
            return Text("enormous")

    def get_full_description(self) -> Text:
        description = Text()
        description.append(self.get_name())
        description.append(" (")
        
        # Handle adjectives
        if self.adjectives:
            adj_text = Text(", ").join([Text(adj, style="italic") for adj in self.adjectives])
            description.append(adj_text)
            description.append(", ")
        
        description.append(self.get_size_description())
        description.append(").\n\n")
        description.append(self.description)
        description.append("\n\n")

        if self.items:
            description.append("Items in the room:\n")
            for item in self.items:
                description.append("- ")
                description.append(item.get_full_description())
                description.append("\n")
        else:
            description.append("There are no items in this room.\n")

        return description
