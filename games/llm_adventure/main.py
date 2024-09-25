import json

import re
import json
import random

import asyncio
from utils.llms.gpt import prompt_completion_chat, prompt_completion_json
from utils.gui.display_interface import show_narrative_text, get_user_text, show_rule_text, show_error, show_situation, start_display, stop_display
from conversation import Conversation, Turn
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

def check_skill(skill, difficulty):
    # Get player's skill level
    skill_json = prompt_completion_json(
        messages=[
            {"role": "system", "content": f"Provide the player's skill level for {skill} as a JSON object with a 'skill_level' key. The value should be between -10 and 10."},
            {"role": "user", "content": f"What is the player's skill level in {skill}?"}
        ]
    )
    skill_data = json.loads(skill_json)
    skill_level = skill_data.get('skill_level', 0)
    
    # Generate a random number for the skill check
    check_result = random.randint(1, 20)
    total_result = check_result + skill_level
    
    # Determine success or failure
    success = total_result >= difficulty * 2
    
    return skill_level, check_result, total_result, success


def get_game_response(conversation):
    while True:
        response = prompt_completion_chat(
            model="gpt-3.5-turbo",
            max_tokens=150,
            messages=conversation.get_messages()
        )

        if "NEED" not in response:
            conversation.add_turn("assistant", response)
            show_narrative_text(response, "Game")
            return

        parts = response.split("NEED", 1)
        conversation.add_turn("assistant", parts[0])
        show_narrative_text(parts[0], "Game")

        need_match = re.search(r"(\w+) (\d+)", parts[1])
        if need_match:
            skill = need_match.group(1)
            difficulty = int(need_match.group(2))

            skill_level, check_result, total_result, success = check_skill(skill, difficulty)

            narrative_text = (
                f"Skill Check: {skill} (Difficulty: {difficulty})\n"
                f"Player's {skill} level: {skill_level}\n"
                f"Dice Roll: {check_result}\n"
                f"Total Result: {total_result}\n"
                f"{'Success!' if success else 'Failure.'}"
            )

            conversation.add_turn("assistant", narrative_text)
            show_narrative_text(narrative_text, "Skill Check!")

            result_text = f"{skill.upper()} check result: {'Success' if success else 'Failure'}"
            conversation.add_turn("assistant", result_text)
            show_narrative_text(result_text, "Game")
        else:
            error_message = f"Failed to parse skill check: NEED{parts[1]}"
            show_error(error_message)
            # conversation.add_turn("assistant", error_message)


def main_loop(conversation, situation):
    last_user_input = ""
    while True:
        situation_json = situation.to_json()
        conversation.update_situation(situation_json)

        get_game_response(conversation)

        last_turn = conversation.history[-1]
        situation = update_situation(situation, last_turn.content, last_user_input)
        show_situation(situation.get_situation_string())

        user_input = get_user_text("What do you want to do? ")

        if user_input.lower() == 'quit':
            show_narrative_text("Thanks for playing!")
            break

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
