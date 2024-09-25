import os

def load_prompt(filename, base_path='games/llm_adventure/prompts'):
    with open(os.path.join(base_path, filename), 'r') as file:
        return file.read().strip()
