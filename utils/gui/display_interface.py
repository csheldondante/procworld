from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.text import Text
from rich.box import DOUBLE

console = Console()

def show_narrative_text(text: str, speaker: str="", color: str = "green") -> None:
    """
    Display a block of narrative text in the console.
    """
    content = Text(text)
    if speaker:
        panel = Panel(content, border_style=color, expand=False, title=speaker, title_align="left")
    else:
        panel = Panel(content, border_style=color, expand=False)
    console.print(panel)

def get_user_text(prompt: str) -> str:
    """
    Get text input from the user.
    """
    return console.input(f"> {prompt}")

def show_rule_text(text: str, rule: str = "") -> None:
    """
    Display a block of text with a rule name in the console.
    """
    content = Text(text)
    title = "Game Rules" if rule else None
    panel = Panel(content, border_style="yellow", box=DOUBLE, expand=False, title=title, title_align="center")
    console.print(panel)

def show_error(error_message: str) -> None:
    """
    Display an error message in the console.
    """
    panel = Panel(Text(error_message), border_style="red", title="Error", title_align="center", expand=False)
    console.print(panel)

def show_situation(situation_text: str) -> None:
    """
    Display the current situation details in the console.
    """
    panel = Panel(
        Text(situation_text),
        border_style="cyan",
        box=DOUBLE,
        expand=False,
        title="Current Situation",
        title_align="right"
    )
    console.print(panel)

def start_display():
    console.clear()

def stop_display():
    pass
