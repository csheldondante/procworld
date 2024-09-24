import rich
from rich.console import Console

console = Console()

def show_narrative_text(text: str, speaker: str="") -> None:
    """
    Display a block of narrative text in the GUI.
    """
    if not speaker or speaker == "":
        console.print(text)
    else:
        console.print(f"[bold]{speaker}[/bold]: {text}")

def get_user_text(prompt: str) -> str:
    """
    Get text input from the user.
    """
    return console.input(prompt)

def show_rule_text(text: str, rule: str = "") -> None:
    """
    Display a block of text with a rule name in the GUI.
    """
    if not rule or rule == "":
        console.print(text)
    else:
        console.print(f"[bold]{rule}[/bold]: {text}")