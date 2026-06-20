import click
from cli.utils.output import (
    console, print_success, print_error,
    print_info, prompt_master_password,
)
from core.vault import VaultManager
from exceptions import AuthenticationError, VaultNotInitializedError, RateLimitError


@click.command()
@click.option("--password", "-p", help="Master password (omit for prompt)")
def auth(password):
    """Authenticate to the vault (establishes a 30-min session)."""
    vault = VaultManager()

    try:
        if not password:
            console.print("  [bold #D39CE0]Master Password:[/bold #D39CE0]")
            from getpass import getpass
            password = getpass("  ")

        vault.authenticate(password)
        print_success("Authenticated")
        print_info("Session expires in 30 minutes")
        print_info("[OPEN] Vault unlocked. Ready to use.")
    except VaultNotInitializedError as e:
        print_error(str(e))
        print_info("Run 'aegis setup' first to create your vault")
        raise SystemExit(1)
    except (AuthenticationError, RateLimitError) as e:
        print_error(str(e))
        raise SystemExit(1)
