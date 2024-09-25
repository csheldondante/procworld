import json
import random
from utils.llms.gpt import prompt_completion_json
from utils.text_utils.prompting import load_prompt

def generate_random_words(num_words=3):
    word_list = [
        "ancient", "mystic", "brave", "cunning", "swift", "wise", "strong", "agile", "clever", "noble",
        "fierce", "gentle", "mysterious", "charismatic", "resilient", "arcane", "ethereal", "valiant",
        "stealthy", "enchanted", "cosmic", "cybernetic", "draconic", "eldritch", "fey", "galactic",
        "heroic", "immortal", "jovial", "knightly", "legendary", "magical", "necromantic", "otherworldly",
        "prophetic", "quantum", "radiant", "shadowy", "telepathic", "undying", "venerable", "wondrous",
        "xenomorphic", "youthful", "zealous", "astral", "bionic", "celestial", "demonic", "elemental",
        "futuristic", "ghostly", "holographic", "interstellar", "juggernaut", "kinetic", "lunar",
        "metamorphic", "nanotech", "omniscient", "phantasmal", "quixotic", "robotic", "sorcerous",
        "time-bending", "unearthly", "void-touched", "warp-powered", "xenotech", "yin-yang", "zephyr-like"
    ]
    return random.sample(word_list, num_words)

def create_character():
    character_prompt = load_prompt('character_prompt.txt')
    inspiration_words = generate_random_words()
    
    messages = [
        {"role": "system", "content": character_prompt},
        {"role": "user", "content": f"Create a character inspired by these words: {', '.join(inspiration_words)}"}
    ]
    
    character_json = prompt_completion_json(messages)
    
    if character_json:
        try:
            character_data = json.loads(character_json)
            return character_data
        except json.JSONDecodeError:
            print("Error: Invalid JSON received from the model.")
    else:
        print("Error: Failed to generate character data.")
    
    return None
