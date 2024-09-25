from utils.llms.gpt import prompt_completion_chat
from utils.gui.display_interface import show_narrative_text, get_user_text, show_rule_text

class Conversation:
    def __init__(self):
        self.context = "You are in a text-based adventure game. Describe the player's surroundings and ask what they want to do."
        self.history = []

    def add_message(self, role, content):
        self.history.append({"role": role, "content": content})
        self.context += f"\n{role.capitalize()}: {content}"

    def get_context(self):
        return self.context

def main_loop(conversation):
    while True:
        response = prompt_completion_chat(
            question=conversation.get_context(),
            model="gpt-3.5-turbo",
            max_tokens=150
        )
        
        show_narrative_text(response, "Game")
        conversation.add_message("Game", response)
        
        user_input = get_user_text("What do you want to do? ")
        
        if user_input.lower() == 'quit':
            show_narrative_text("Thanks for playing!")
            break
        
        conversation.add_message("Player", user_input)

def main_start():
    show_rule_text("Welcome to the LLM Adventure Game!", "Game Rules")
    show_rule_text("Type 'quit' to exit the game.", "Game Rules")
    
    conversation = Conversation()
    main_loop(conversation)

if __name__ == "__main__":
    main_start()
