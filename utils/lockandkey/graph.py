from typing import Dict, List, Optional
from games.walk_and_key.room_and_door import Room, Door
from games.walk_and_key.lock import Lock

class Node:
    def __init__(self, id):
        self.id = id
        self.edges = []

    def add_edge(self, edge):
        self.edges.append(edge)

    def connect_node(self, target, weight=1):
        edge = Edge(self, target, weight)
        self.add_edge(edge)
        target.add_edge(edge)

    def get_neighbors(self):
        return [edge.target if edge.source == self else edge.source for edge in self.edges]

class Edge:
    def __init__(self, source, target, weight=1):
        self.source = source
        self.target = target
        self.weight = weight

class Graph:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.rooms: List[Room] = []

    def add_node(self, node):
        self.nodes[node.id] = node

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

    def get_neighboring_rooms(self, room: Room) -> List[Room]:
        neighboring_rooms = []
        for door in room.doors.values():
            neighboring_room = door.room1 if door.room2 == room else door.room2
            neighboring_rooms.append(neighboring_room)
        return neighboring_rooms

    def get_doors_for_room(self, room: Room) -> List[Door]:
        return list(room.doors.values())

    def all_doors(self):
        visited_doors = set()
        for room in self.rooms:
            for door in room.doors.values():
                if door not in visited_doors:
                    visited_doors.add(door)
                    yield door

    def remove_locked_doors_with_no_key(self):
        for room in self.rooms:
            room.doors = {direction: door for direction, door in room.doors.items() if not door.is_locked_with_no_key()}

class RectangularGrid(Graph):
    def __init__(self, rows, cols):
        super().__init__()
        self.rows = rows
        self.cols = cols

def generate_rectangular_grid(rows, cols):
    grid = RectangularGrid(rows, cols)

    # Create nodes
    for i in range(rows):
        for j in range(cols):
            node_id = f"{i},{j}"
            grid.add_node(Node(node_id))

    # Create edges
    for i in range(rows):
        for j in range(cols):
            current_node = grid.nodes[f"{i},{j}"]

            # Add edge to the right
            if j < cols - 1:
                right_node = grid.nodes[f"{i},{j+1}"]
                current_node.connect_node(right_node)

            # Add edge down
            if i < rows - 1:
                down_node = grid.nodes[f"{i+1},{j}"]
                current_node.connect_node(down_node)

    return grid

if __name__ == "__main__":
    grid = generate_rectangular_grid(3, 3)
    print(grid.nodes)
    print(grid.nodes["0,0"].get_neighbors())
    print(grid.nodes["1,1"].get_neighbors())
    print(grid.nodes["2,2"].get_neighbors())
    print(grid.nodes["1,2"].get_neighbors())
    print(grid.nodes["2,1"].get_neighbors())
