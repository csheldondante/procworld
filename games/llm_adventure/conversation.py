from utils.text_utils.prompting import load_prompt

class Turn:
    def __init__(self, role, content):
        self.role = role
        self.content = content

class Conversation:
    def __init__(self):
        self.system_message = {"role": "system", "content": load_prompt('system_prompt.txt')}
        self.situation_message = {"role": "system", "content": ""}
        self.history = []

    def add_turn(self, role, content):
        self.history.append(Turn(role, content))

    def update_situation(self, situation_string):
        self.situation_message["content"] = situation_string

    def get_messages(self):
        messages = [self.system_message, self.situation_message]
        for turn in self.history:
            role = turn.role if turn.role in ["system", "user", "assistant"] else "user"
            messages.append({"role": role, "content": turn.content})
        return messages
