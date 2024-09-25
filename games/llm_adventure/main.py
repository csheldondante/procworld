from utils.llms.gpt import prompt_completion_chat
from utils.gui.display_interface import show_narrative_text, get_user_text, show_rule_text

class Turn:
    def __init__(self, role, content):
        self.role = role
        self.content = content

class Conversation:
    def __init__(self):
        self.system_message = {"role": "system", "content": "You are in a text-based adventure game. Describe the player's surroundings and ask what they want to do."}
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
    show_rule_text("Welcome to the LLM Adventure Game!", "Game Rules")
    show_rule_text("Type 'quit' to exit the game.", "Game Rules")
    
    conversation = Conversation()
    main_loop(conversation)

if __name__ == "__main__":
    main_start()
