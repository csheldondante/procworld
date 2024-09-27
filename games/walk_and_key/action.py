from enum import Enum, auto

class ActionType(Enum):
    MOVE = auto()
    PICK_UP = auto()
    USE = auto()
    QUIT = auto()

class Action:
    def __init__(self, action_type, target, description):
        self.action_type = action_type
        self.target = target
        self.description = description

    def __str__(self):
        return self.description
