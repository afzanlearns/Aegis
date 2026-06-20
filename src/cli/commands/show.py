import sys
import click
from cli.utils.output import console, print_error
from core.vault import VaultManager
from exceptions import SecretNotFoundError, DecryptionError


@click.command()
@click.argument("name")
def show(name):
    """Retrieve and copy a secret to clipboard."""
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
        vault.get_secret(name, copy=True)
        console.print(f"  [bold #4CAF50][OK][/bold #4CAF50] Retrieved '[bold]{name}[/bold]'")
        console.print("  [bold #FFC107][COPY][/bold #FFC107] Copied to clipboard (clears in 30s)")
    except SecretNotFoundError as e:
        print_error(str(e))
        sys.exit(1)
    except DecryptionError as e:
        print_error(str(e))
        sys.exit(1)
