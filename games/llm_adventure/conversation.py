from utils.text_utils.prompting import load_prompt

class Turn:
    def __init__(self, role, content):
        self.role = role
        self.content = content

class Conversation:
    def __init__(self):
        self.system_message = {"role": "system", "content": load_prompt('system_prompt.txt')}
        self.history = []

    def add_turn(self, role, content):
        self.history.append(Turn(role, content))

    def get_messages(self):
        messages = [self.system_message]
        for turn in self.history:
            role = turn.role if turn.role in ["system", "user", "assistant"] else "user"
            messages.append({"role": role, "content": turn.content})
        return messages
