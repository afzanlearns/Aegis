import sys
import click
from cli.utils.output import console, print_error, print_info
from core.vault import VaultManager
from exceptions import SecretNotFoundError


@click.command()
@click.argument("name")
def delete(name):
    """Delete a stored secret."""
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

    try:
        click.confirm(
            f"  [bold #FFC107]Delete '{name}'?[/bold #FFC107]",
            abort=True,
        )
    except click.Abort:
        print_info("Cancelled")
        return

    try:
        vault.delete_secret(name)
        console.print(f"  [bold #4CAF50][OK][/bold #4CAF50] Deleted '[bold]{name}[/bold]'")
    except SecretNotFoundError as e:
        print_error(str(e))
        sys.exit(1)
