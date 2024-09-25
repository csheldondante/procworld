from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.text import Text
from rich.style import Style

console = Console()

def show_narrative_text(text: str, speaker: str="") -> None:
    """
    Display a block of narrative text in the GUI.
    """
    content = Text(text)
    if not speaker or speaker == "":
        panel = Panel(content, border_style="cyan", expand=False)
    else:
        speaker_style = Style(color="yellow", bold=True)
        content = Text.assemble((f"{speaker}: ", speaker_style), content)
        panel = Panel(content, border_style="green", expand=False)
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
        panel = Panel(content, border_style="blue", expand=False)
    else:
        rule_style = Style(color="red", bold=True)
        content = Text.assemble((f"{rule}\n", rule_style), content)
        panel = Panel(content, border_style="blue", title="Game Rules", expand=False)
    console.print(panel)
