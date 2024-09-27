from typing import List, Dict, Optional
from rich.text import Text
from games.walk_and_key.lock import Lock
from games.walk_and_key.item import Item
from games.walk_and_key.lockandkeyplayer import LockAndKeyPlayer

class Room:
    def __init__(self, name: str, room_type: str, size: int, adjectives: List[str], description: str, x: int = -1, y: int = -1):
        self.name: str = name
        self.room_type: str = room_type
        self.size: int = size
        self.adjectives: List[str] = adjectives
        self.description: str = description
        self.doors: Dict[str, 'Door'] = {}  # direction -> Door
        self.items: List[Item] = []
        self.x: int = x
        self.y: int = y
        self.visited: bool = False

    def add_door(self, direction: str, door: 'Door') -> None:
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
            adj_text = Text(", ").join([Text(adj, style="") for adj in self.adjectives])  # Style italic
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

class Door:
    def __init__(self, room1: 'Room', room2: 'Room', direction: str, lock: Optional[Lock] = None):
        self.room1: 'Room' = room1
        self.room2: 'Room' = room2
        self.direction: str = direction
        self.lock: Optional[Lock] = lock
    
    def is_locked(self) -> bool:
        return self.lock is not None

    def unlock(self) -> None:
        self.lock = None

    def can_unlock(self, key: Item) -> bool:
        return self.lock and self.lock.color == key.color

    def can_player_unlock(self, player: LockAndKeyPlayer) -> bool:
        return any(self.can_unlock(key) for key in player.inventory)

    def get_lock_description_short(self) -> Text:
        if self.lock:
            description = Text()
            description.append("Locked with a ")
            description.append(self.lock.name, style=f"bold {self.lock.color}")
            return description
        return Text("Unlocked")

    def get_lock_description(self) -> Text:
        if self.lock:
            description = Text()
            description.append("The door is locked with a ")
            description.append(self.lock.name, style=f"bold {self.lock.color}")
            description.append(f". {self.lock.description}")
            return description
        return Text("The door is unlocked.")
