import click
from cli.utils.output import console, print_vault_panel, print_success, print_info, print_error
from core.vault import VaultManager


@click.command()
def logout():
    """End the current session and lock the vault."""
    vault = VaultManager()
    vault.logout()

    print_vault_panel(
        "logout",
        "\n  [bold #4CAF50]✓ Session ended[/bold #4CAF50]\n"
        "\n  [dim]🔒 Vault locked.[/dim]\n",
    )
