class Player:
    def __init__(self, name):
        self.name = name
        self.race = ""
        self.class_ = ""
        self.background = ""
        self.stats = {"health": 100, "strength": 10, "dexterity": 10, "constitution": 10, "intelligence": 10, "wisdom": 10, "charisma": 10}
        self.skills = []
        self.inventory = []
        self.backstory = ""

    def update_from_character_data(self, character_data):
        self.name = character_data['name']
        self.race = character_data['race']
        self.class_ = character_data['class']
        self.background = character_data['background']
        self.stats.update(character_data['stats'])
        self.skills = character_data['skills']
        self.inventory = character_data['equipment']
        self.backstory = character_data['backstory']

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
        situation += f"Player: {self.player.name} ({self.player.race} {self.player.class_})\n"
        situation += f"Player Stats: {self.player.stats}\n"
        situation += f"Player Skills: {', '.join(self.player.skills)}\n"
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
                "race": self.player.race,
                "class": self.player.class_,
                "background": self.player.background,
                "stats": self.player.stats,
                "skills": self.player.skills,
                "inventory": self.player.inventory,
                "backstory": self.player.backstory
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
        situation.player.race = data["player"]["race"]
        situation.player.class_ = data["player"]["class"]
        situation.player.background = data["player"]["background"]
        situation.player.stats = data["player"]["stats"]
        situation.player.skills = data["player"]["skills"]
        situation.player.inventory = data["player"]["inventory"]
        situation.player.backstory = data["player"]["backstory"]
        situation.nearby_monsters = [
            Monster(monster["name"], monster["health"])
            for monster in data["nearby_monsters"]
        ]
        return situation
