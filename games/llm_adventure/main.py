import json
from utils.llms.gpt import prompt_completion_chat, prompt_completion_json
from utils.gui.display_interface import show_narrative_text, get_user_text, show_rule_text, show_error, show_situation, start_display, stop_display
from conversation import Conversation
from situation import Situation

def update_situation(current_situation, response, last_user_input):
    situation_json = current_situation.to_json()
    new_situation_json = prompt_completion_json(
        messages=[
            {"role": "system", "content": "Given the current situation, the game's response, and the user's last input, provide an updated situation as a JSON object."},
            {"role": "user", "content": f"Current situation: {situation_json}\nGame response: {response}\nLast user input: {last_user_input}"}
        ]
    )
    
    if new_situation_json:
        try:
            return Situation.from_json(new_situation_json)
        except json.JSONDecodeError:
            show_error("Invalid JSON received from the model. Keeping the current situation.")
    else:
        show_error("Failed to generate new situation. Keeping the current situation.")
    
    return current_situation

async def main_loop(conversation, situation):
    last_user_input = ""
    while True:
        situation_json = situation.to_json()
        conversation.update_situation(situation_json)
        
        response = prompt_completion_chat(
            model="gpt-3.5-turbo",
            max_tokens=150,
            messages=conversation.get_messages()
        )
        
        show_narrative_text(response, "Game")
        conversation.add_turn("assistant", response)
        
        situation = update_situation(situation, response, last_user_input)
        show_situation(situation.get_situation_string())
        
        user_input = await get_user_text("What do you want to do? ")
        
        if user_input.lower() == 'quit':
            show_narrative_text("Thanks for playing!")
            break
        
        show_narrative_text(user_input, "You")
        conversation.add_turn("user", user_input)
        last_user_input = user_input

def main_start():
    start_display()
    welcome_message = "Welcome to the LLM Adventure Game!\nType 'quit' to exit the game."
    show_rule_text(welcome_message, "Game Rules")
    
    conversation = Conversation()
    situation = Situation()
    situation.add_monster("Goblin", 50)
    show_situation(situation.get_situation_string())

    main_loop(conversation, situation)

if __name__ == "__main__":
    main_start()
