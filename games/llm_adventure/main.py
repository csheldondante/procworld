from utils.llms.gpt import prompt_completion_chat
from utils.gui.display_interface import show_narrative_text, get_user_text, show_rule_text
from conversation import Conversation
from situation import Situation

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
