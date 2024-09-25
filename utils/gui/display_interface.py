from rich import print
from rich.panel import Panel
from rich.console import Console, Group
from rich.text import Text
from rich.style import Style
from rich.box import DOUBLE, ROUNDED
from rich.columns import Columns
from rich.live import Live

console = Console()
left_column = []
right_column = []
live_display = Live(Group(), console=console, refresh_per_second=4, screen=True)

def update_display():
    global live_display
    live_display.update(
        Columns(
            [
                Panel(Group(*left_column), expand=True, width=console.width // 2),
                Panel(Group(*right_column), expand=True, width=console.width // 2)
            ],
            expand=True
        )
    )

def show_narrative_text(text: str, speaker: str="", color: str = "green") -> None:
    """
    Display a block of narrative text in the GUI.
    """
    content = Text(text)
    if not speaker or speaker == "":
        panel = Panel(content, border_style=color, expand=False)
    else:
        panel = Panel(content, border_style=color, expand=False,
                      title=speaker, title_align="left")
    left_column.append(panel)
    update_display()

def get_user_text(prompt: str) -> str:
    """
    Get text input from the user.
    """
    live_display.stop()
    user_input = console.input(f"[bold magenta]> {prompt}[/bold magenta]")
    live_display.start()
    return user_input

def show_rule_text(text: str, rule: str = "") -> None:
    """
    Display a block of text with a rule name in the GUI.
    """
    content = Text(text)
    if not rule or rule == "":
        panel = Panel(content, border_style="yellow", box=DOUBLE, expand=False)
    else:
        panel = Panel(content, border_style="yellow", box=DOUBLE, title="Game Rules", 
                      title_align="center", expand=False)
    left_column.append(panel)
    update_display()

def show_error(error_message: str) -> None:
    """
    Display an error message in the GUI.
    """
    content = Text(error_message)
    panel = Panel(content, border_style="red", title="Error", title_align="center", expand=False)
    left_column.append(panel)
    update_display()

def show_situation(situation_text: str) -> None:
    """
    Display the current situation details in the GUI.
    """
    content = Text(situation_text)
    panel = Panel(
        content,
        border_style="cyan",
        box=DOUBLE,
        expand=False,
        title="Current Situation",
        title_align="right"
    )
    right_column.clear()  # Clear previous situation
    right_column.append(panel)
    update_display()

def start_display():
    global live_display
    live_display.start()

def stop_display():
    global live_display
    live_display.stop()
