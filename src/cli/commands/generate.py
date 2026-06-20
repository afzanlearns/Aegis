import click
from cli.utils.output import console
from core.vault import VaultManager


@click.command()
@click.argument("length", default=32, type=int)
def generate(length):
    """Generate a random password.

    Usage: aegis generate [LENGTH]

    Examples:

      aegis generate        32 character password

      aegis generate 16     16 character password

      aegis generate 64     64 character password
    """
    vault = VaultManager()
    password = vault.generate_password(length=length, symbols=True)
    console.print(f"  [bold #FFFFFF]{password}[/bold #FFFFFF]")
