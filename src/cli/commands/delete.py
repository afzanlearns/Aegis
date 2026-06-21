import sys
import click
from cli.utils.output import console, CleanCommand
from core.vault import VaultManager
from exceptions import SecretNotFoundError


@click.command(cls=CleanCommand)
@click.argument("name")
def delete(name):
    """Delete a secret permanently.

    You will be asked to confirm before deletion.

    Arguments:
      NAME              Name of the secret to delete

    Examples:
      aegis delete github-token
      aegis delete old-api-key
    """
    vault = VaultManager()

    if not vault.is_authenticated():
        console.print("  [bold #FFC107][WARN][/bold #FFC107] Not authenticated")
        console.print("  [dim][*] Run: aegis auth[/dim]")
        sys.exit(1)

    try:
        click.confirm(
            f"  [bold #FFC107]Delete '{name}'?[/bold #FFC107]",
            abort=True,
        )
    except click.Abort:
        console.print("  [bold #D39CE0][*][/bold #D39CE0] Cancelled")
        return

    try:
        vault.delete_secret(name)
        console.print(f"  [bold #4CAF50][OK][/bold #4CAF50] Deleted '[bold]{name}[/bold]'")
    except SecretNotFoundError as e:
        console.print(f"  [bold #FF5252][ERR][/bold #FF5252] {e}")
        sys.exit(1)
