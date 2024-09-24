from lockandkey.graph import generate_rectangular_grid, Graph

graph: Graph = generate_rectangular_grid(4, 4)

class Player:
    def __init__(self, pos):
        self.pos = pos
        self.inventory = []


class LockAndKey:
    def __init__(self):
        self.objects: list[str] = []
        self.lock_to_keys: dict[str, list[str]] = {}

# Journey Algorithm
