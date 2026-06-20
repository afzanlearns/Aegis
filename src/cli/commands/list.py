import click
from cli.utils.output import (
    console, print_vault_panel, print_secret_list, print_error, print_info,
)
from core.vault import VaultManager
from exceptions import AuthenticationError


@click.command()
def list_secrets():
    """List all stored secrets (values redacted)."""
    vault = VaultManager()

    try:
        secrets = vault.list_secrets()

        if secrets:
            count = len(secrets)
            print_vault_panel(
                "list",
                f"\n  [bold #D39CE0]🔐 Your Secrets ({count} stored)[/bold #D39CE0]\n",
            )
            print_secret_list(secrets)
            print_info("")
            print_info("💡 Tip: aegis get <name> --copy")
        else:
            print_vault_panel(
                "list",
                "\n  🔐 No secrets stored yet.\n\n  💡 Save your first secret: aegis save <name> <value>\n",
                border_color="#FFC107",
            )
    except AuthenticationError as e:
        print_error(str(e))
        print_info("Run 'aegis auth' first")
        raise SystemExit(1)
