class Player:
    def __init__(self, name):
        self.name = name
        self.stats = {"health": 100, "strength": 10, "agility": 10}
        self.inventory = []

class Monster:
    def __init__(self, name, health):
        self.name = name
        self.health = health

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
        return situation
