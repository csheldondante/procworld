from utils.llms.gpt import prompt_completion_chat
from utils.gui.display_interface import show_narrative_text, get_user_text, show_rule_text
from utils.text_utils.prompting import load_prompt

class Situation:
    def __init__(self):
        self.world = "world1"
        self.location = "Caverns of Echo"

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

def main_loop(conversation):
    while True:
        response = prompt_completion_chat(
            model="gpt-3.5-turbo",
            max_tokens=150,
            messages=conversation.get_messages(),
            system_description=conversation.system_message["content"]
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
    main_loop(conversation)

if __name__ == "__main__":
    main_start()
