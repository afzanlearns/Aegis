import click
from cli.utils.output import console, CleanCommand
from core.vault import VaultManager


@click.command(cls=CleanCommand)
def lock():
    """Lock the vault and end session.

    Examples:
      aegis lock
      [OK] Session ended
      [LOCK] Vault locked
    """
    vault = VaultManager()
    vault.logout()
    console.print("  [bold #4CAF50][OK][/bold #4CAF50] Vault locked")
