from rich.text import Text
from typing import List

class Item:
    def __init__(self, name: str, color: str, adjectives: List[str], description: str, biomes: List[str]):
        self.name = name
        self.color = color
        self.adjectives = adjectives
        self.description = description
        self.biomes = biomes

    def get_name(self) -> Text:
        return Text(self.name, style=f"bold {self.color}")

    def get_full_description(self) -> Text:
        description = Text()
        description.append(self.get_name())
        if self.adjectives:
            description.append(" (")
            description.append(", ".join([Text(adj, style="").plain for adj in self.adjectives]))  # Style italic
            description.append(")")
        description.append(f": {self.description}")
        return description

    def __eq__(self, other):
        if isinstance(other, Item):
            return self.name == other.name and self.color == other.color
        return False

    def __hash__(self):
        return hash((self.name, self.color))
