import json
from utils.llms.gpt import prompt_completion_chat, prompt_completion_json
from utils.gui.display_interface import show_narrative_text, get_user_text, show_rule_text
from conversation import Conversation
from situation import Situation

def main_loop(conversation, situation):
    last_user_input = ""
    while True:
        situation_json = situation.to_json()
        show_narrative_text(situation.get_situation_string(), "Situation")
        conversation.update_situation(situation_json)
        
        response = prompt_completion_chat(
            model="gpt-3.5-turbo",
            max_tokens=150,
            messages=conversation.get_messages()
        )
        
        show_narrative_text(response, "Game")
        conversation.add_turn("assistant", response)
        
        user_input = get_user_text("What do you want to do? ")
        
        if user_input.lower() == 'quit':
            show_narrative_text("Thanks for playing!")
            break
        
        conversation.add_turn("user", user_input)
        
        # Get new situation based on model response and user input
        new_situation_json = prompt_completion_json(
            messages=[
                {"role": "system", "content": "Given the current situation, the game's response, and the user's input, provide an updated situation as a JSON object."},
                {"role": "user", "content": f"Current situation: {situation_json}\nGame response: {response}\nUser input: {user_input}"}
            ]
        )
        
        if new_situation_json:
            try:
                situation = Situation.from_json(new_situation_json)
            except json.JSONDecodeError:
                print("Error: Invalid JSON received from the model. Keeping the current situation.")
        
        last_user_input = user_input

def main_start():
    welcome_message = "Welcome to the LLM Adventure Game!\nType 'quit' to exit the game."
    show_rule_text(welcome_message, "Game Rules")
    
    conversation = Conversation()
    situation = Situation()
    situation.add_monster("Goblin", 50)
    main_loop(conversation, situation)

if __name__ == "__main__":
    main_start()
