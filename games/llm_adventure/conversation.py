from utils.text_utils.prompting import load_prompt

class Turn:
    def __init__(self, role, content):
        self.role = role
        self.content = content

class Conversation:
    def __init__(self):
        self.system_message = {"role": "system", "content": load_prompt('system_prompt.txt')}
        self.situation_message = ""
        self.history = []

    def add_turn(self, role, content):
        self.history.append(Turn(role, content))

    def update_situation(self, situation_string):
        self.situation_message = f"Current situation:\n{situation_string}"

    def get_messages(self):
        messages = [self.system_message]
        for turn in self.history:
            role = "user" if turn.role == "user" else "assistant"
            messages.append({"role": role, "content": turn.content})
        messages.append({"role": "assistant", "content": self.situation_message})
        return messages
