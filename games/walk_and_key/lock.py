from typing import List
from rich.text import Text

class Lock:
    def __init__(self, name: str, color: str, adjectives: List[str], description: str, biomes: List[str]):
        self.name: str = name
        self.color: str = color
        self.adjectives: List[str] = adjectives
        self.description: str = description
        self.biomes: List[str] = biomes

    def get_name(self) -> Text:
        return Text(self.name, style=f"bold {self.color}")

    def get_description(self) -> Text:
        description = Text()
        description.append(self.description)
        # Add adjectives
        if self.adjectives:
            description.append(" ")
            description.append(" ".join(self.adjectives), style="")  # Style italic
        return description
