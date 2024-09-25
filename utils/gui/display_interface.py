from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.text import Text
from rich.style import Style
from rich.box import DOUBLE

console = Console()

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
    console.print(panel)

def get_user_text(prompt: str) -> str:
    """
    Get text input from the user.
    """
    return console.input(f"[bold magenta]> {prompt}[/bold magenta]")

def show_rule_text(text: str, rule: str = "") -> None:
    """
    Display a block of text with a rule name in the GUI.
    """
    content = Text(text)
    if not rule or rule == "":
        panel = Panel(content, border_style="yellow", box=DOUBLE, expand=False)
    else:
        rule_style = Style(color="yellow", bold=True)
        panel = Panel(content, border_style="yellow", box=DOUBLE, title="Game Rules", 
                      title_align="center", expand=False)
    console.print(panel)
