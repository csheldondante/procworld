class Player:
    def __init__(self, name):
        self.name = name
        self.stats = {"health": 100, "strength": 10, "agility": 10}
        self.inventory = []

class Monster:
    def __init__(self, name, health):
        self.name = name
        self.health = health

import json

class Situation:
    def __init__(self):
        self.world = "world1"
        self.location = "Caverns of Echo"
        self.player = Player("Hero")
        self.nearby_monsters = []

    def add_monster(self, name, health):
        self.nearby_monsters.append(Monster(name, health))

    def get_situation_string(self):
        situation = f"World: {self.world}\n"
        situation += f"Location: {self.location}\n"
        situation += f"Player: {self.player.name}\n"
        situation += f"Player Stats: {self.player.stats}\n"
        situation += f"Player Inventory: {', '.join(self.player.inventory)}\n"
        if self.nearby_monsters:
            situation += "Nearby Monsters:\n"
            for monster in self.nearby_monsters:
                situation += f"- {monster.name} (Health: {monster.health})\n"
        return situation.strip()

    def to_json(self):
        return json.dumps({
            "world": self.world,
            "location": self.location,
            "player": {
                "name": self.player.name,
                "stats": self.player.stats,
                "inventory": self.player.inventory
            },
            "nearby_monsters": [
                {"name": monster.name, "health": monster.health}
                for monster in self.nearby_monsters
            ]
        })

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        situation = cls()
        situation.world = data["world"]
        situation.location = data["location"]
        situation.player = Player(data["player"]["name"])
        situation.player.stats = data["player"]["stats"]
        situation.player.inventory = data["player"]["inventory"]
        situation.nearby_monsters = [
            Monster(monster["name"], monster["health"])
            for monster in data["nearby_monsters"]
        ]
        return situation
