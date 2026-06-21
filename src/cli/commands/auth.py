import sys
import click
from cli.utils.output import console, CleanCommand
from core.vault import VaultManager
from exceptions import AuthenticationError, VaultNotInitializedError, RateLimitError


@click.command(cls=CleanCommand)
@click.option("--password", "-p", help="Master password (omit for prompt)")
def auth(password):
    """Authenticate to the vault (creates 30-minute session).

    Master password is required.

    Options:
      -p, --password TEXT   Master password (omit for secure prompt)

    Examples:
      aegis auth
      aegis auth -p MySecretPass123
    """
    vault = VaultManager()

    try:
        if not password:
            console.print("  [bold #D39CE0]Master Password:[/bold #D39CE0]")
            from getpass import getpass
            password = getpass("  ")

        vault.authenticate(password)
        console.print("  [bold #4CAF50][OK][/bold #4CAF50] Authenticated (expires in 30 minutes)")
    except VaultNotInitializedError as e:
        console.print(f"  [bold #FF5252][ERR][/bold #FF5252] {e}")
        console.print("  [dim][*] Run 'aegis auth' first to set up your vault[/dim]")
        sys.exit(1)
    except (AuthenticationError, RateLimitError) as e:
        console.print(f"  [bold #FF5252][ERR][/bold #FF5252] {e}")
        sys.exit(1)
