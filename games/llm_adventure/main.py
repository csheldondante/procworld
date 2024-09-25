from utils.llms.gpt import prompt_completion_chat
from utils.gui.display_interface import show_narrative_text, get_user_text, show_rule_text
from utils.text_utils.prompting import load_prompt

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

class Turn:
    def __init__(self, role, content):
        self.role = role
        self.content = content

class Conversation:
    def __init__(self):
        self.system_message = {"role": "system", "content": load_prompt('system_prompt.txt')}
        self.history = []

    def add_turn(self, role, content):
        self.history.append(Turn(role, content))

    def get_messages(self):
        messages = [self.system_message]
        for turn in self.history:
            role = turn.role if turn.role in ["system", "user", "assistant"] else "user"
            messages.append({"role": role, "content": turn.content})
        return messages

def main_loop(conversation, situation):
    while True:
        situation_string = situation.get_situation_string()
        response = prompt_completion_chat(
            model="gpt-3.5-turbo",
            max_tokens=150,
            messages=conversation.get_messages(),
            system_description=conversation.system_message["content"],
            situation=situation_string
        )
        
        show_narrative_text(response, "Game")
        conversation.add_turn("assistant", response)
        
        user_input = get_user_text("What do you want to do? ")
        
        if user_input.lower() == 'quit':
            show_narrative_text("Thanks for playing!")
            break
        
        conversation.add_turn("user", user_input)

def main_start():
    welcome_message = "Welcome to the LLM Adventure Game!\nType 'quit' to exit the game."
    show_rule_text(welcome_message, "Game Rules")
    
    conversation = Conversation()
    situation = Situation()
    situation.add_monster("Goblin", 50)
    main_loop(conversation, situation)

if __name__ == "__main__":
    main_start()
