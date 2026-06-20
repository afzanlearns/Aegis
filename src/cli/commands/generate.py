import click
from cli.utils.output import console
from core.vault import VaultManager


@click.command()
@click.argument("length", default=32, type=int)
def generate(length):
    """Generate a strong random password."""
    vault = VaultManager()
    password = vault.generate_password(length=length, symbols=True)
    console.print(f"  [bold #FFFFFF]{password}[/bold #FFFFFF]")
