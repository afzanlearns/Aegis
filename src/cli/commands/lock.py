import click
from cli.utils.output import console
from core.vault import VaultManager


@click.command()
def lock():
    """Lock the vault and end the session."""
    vault = VaultManager()
    vault.logout()
    console.print("  [bold #4CAF50][OK][/bold #4CAF50] Vault locked")
