import click
from cli.utils.output import (
    console, print_success,
    print_info, prompt_master_password, print_error,
)
from core.vault import VaultManager
from exceptions import WeakPasswordError


@click.command()
def setup():
    """Initialize vault with master password (first-time setup)."""
    vault = VaultManager()

    try:
        if vault.config_mgr.is_initialized():
            console.print("  Vault already initialized at ~/.aegis/")
            console.print("  Run 'aegis auth' to authenticate.")
            return

        console.print("  [bold #D39CE0]Master Password (12+ chars):[/bold #D39CE0]")
        password = prompt_master_password(confirm=True)

        vault.setup(password)
        print_success("Vault created")
        print_info("Location: ~/.aegis/")
        print_info("")
        print_info("Next: Run 'aegis auth' to authenticate")
    except (WeakPasswordError, ValueError) as e:
        print_error(str(e))
        raise SystemExit(1)
