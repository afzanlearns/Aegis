import click
from cli.utils.output import (
    console, print_header, print_vault_panel, print_success,
    print_info, prompt_master_password, print_error, TEXT,
)
from core.vault import VaultManager
from exceptions import WeakPasswordError
from rich.text import Text


@click.command()
def setup():
    """Initialize vault with master password (first-time setup)."""
    print_header()

    print_vault_panel(
        "setup",
        "\n  [bold #D39CE0]🔐 Creating your vault...[/bold #D39CE0]\n",
    )

    vault = VaultManager()

    try:
        if vault.config_mgr.is_initialized():
            print_vault_panel(
                "setup",
                Text("  Vault already initialized at ~/.aegis/\n\n  Run 'aegis auth' to authenticate.", style=TEXT),
                border_color="#FFC107",
            )
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
