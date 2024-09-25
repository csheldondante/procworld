from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, Container
from textual.widgets import Header, Footer, Static, Input, Button
from textual.reactive import reactive

class GameDisplay(App):
    CSS = """
    Screen {
        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 1fr;
    }

    #left-column, #right-column {
        height: 100%;
        overflow: hidden;
    }

    .narrative, .rule, .error, .situation {
        margin: 1 0;
        padding: 1;
    }

    .narrative {
        border: solid green;
    }

    .rule {
        border: double yellow;
    }

    .error {
        border: solid red;
    }

    .situation {
        border: double cyan;
    }

    #user-input {
        dock: bottom;
    }
    """

    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(ScrollableContainer(id="left-column"), id="left-column")
        yield Container(ScrollableContainer(id="right-column"), id="right-column")
        yield Input(id="user-input", placeholder="What do you want to do?")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#user-input").focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.handle_user_input(event.value)
        event.input.value = ""

    def handle_user_input(self, user_input: str) -> None:
        if user_input.lower() == 'quit':
            self.exit()
        else:
            self.show_narrative_text(user_input, "You")

    def show_narrative_text(self, text: str, speaker: str = "") -> None:
        content = f"[{speaker}] {text}" if speaker else text
        self.query_one("#left-column").mount(Static(content, classes="narrative"))

    def show_rule_text(self, text: str, rule: str = "") -> None:
        content = f"[{rule}] {text}" if rule else text
        self.query_one("#left-column").mount(Static(content, classes="rule"))

    def show_error(self, error_message: str) -> None:
        self.query_one("#left-column").mount(Static(error_message, classes="error"))

    def show_situation(self, situation_text: str) -> None:
        self.query_one("#right-column").query("*").remove()
        self.query_one("#right-column").mount(Static(situation_text, classes="situation"))

def show_narrative_text(text: str, speaker: str = "") -> None:
    app.show_narrative_text(text, speaker)

def get_user_text(prompt: str) -> str:
    return app.run_async(lambda: app.query_one("#user-input").value)

def show_rule_text(text: str, rule: str = "") -> None:
    app.show_rule_text(text, rule)

def show_error(error_message: str) -> None:
    app.show_error(error_message)

def show_situation(situation_text: str) -> None:
    app.show_situation(situation_text)

def start_display():
    global app
    app = GameDisplay()
    app.run()

def stop_display():
    app.exit()

app = None
