import sys
import click
from cli.utils.output import console
from core.vault import VaultManager
from exceptions import SecretNotFoundError, DecryptionError


@click.command()
@click.argument("name")
def show(name):
    """Retrieve a secret and copy it to your clipboard (auto-clears in 30s).

    Usage: aegis show NAME

    Examples:

      aegis show github-token

      aegis show database-password

      aegis show stripe-key

    The secret is copied to clipboard and never displayed on screen.
    Clipboard clears automatically after 30 seconds.
    """
    vault = VaultManager()

    if not vault.is_authenticated():
        console.print("  [bold #FFC107][WARN][/bold #FFC107] Not authenticated")
        console.print("  [dim][*] Run: aegis auth[/dim]")
        sys.exit(1)

    try:
        vault.get_secret(name, copy=True)
        console.print(f"  [bold #4CAF50][OK][/bold #4CAF50] Retrieved '[bold]{name}[/bold]'")
        console.print("  [bold #FFC107][COPY][/bold #FFC107] Copied to clipboard (clears in 30s)")
    except SecretNotFoundError as e:
        console.print(f"  [bold #FF5252][ERR][/bold #FF5252] {e}")
        sys.exit(1)
    except DecryptionError as e:
        console.print(f"  [bold #FF5252][ERR][/bold #FF5252] {e}")
        sys.exit(1)
