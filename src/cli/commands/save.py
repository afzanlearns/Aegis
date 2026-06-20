import sys
import click
from cli.utils.output import console, print_error
from core.vault import VaultManager


@click.command()
@click.argument("name")
@click.argument("tag")
def save(name, tag):
    """Save a secret with a tag."""
    vault = VaultManager()
    if not vault.is_authenticated():
        console.print(
            "[#9C27B0 bold][ERR][/#9C27B0 bold] Not authenticated",
            style="#FF5252"
        )
        console.print(
            "[dim]Run '[#9C27B0]aegis auth[/#9C27B0]' to authenticate[/dim]"
        )
        sys.exit(1)

    from getpass import getpass
    console.print(f"  [bold #D39CE0]Value for '{name}':[/bold #D39CE0]")
    value = getpass("  ")

    if not value:
        print_error("Value cannot be empty")
        sys.exit(1)

    try:
        vault.save_secret(name, value, tag=tag)
        console.print(f"  [bold #4CAF50][OK][/bold #4CAF50] Saved '[bold]{name}[/bold]' [[bold #D39CE0]{tag}[/bold #D39CE0]]")
    except Exception as e:
        print_error(str(e))
        sys.exit(1)
