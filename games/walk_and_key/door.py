from typing import Optional
from rich.text import Text
from games.walk_and_key.lock import Lock
from games.walk_and_key.room import Room

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
