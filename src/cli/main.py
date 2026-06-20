import click
from cli.utils.output import (
    console, print_header, print_error,
)
from core.vault import VaultManager


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Aegis v1.0.0 - Encrypted Secrets Manager"""
    print_header()
    if ctx.invoked_subcommand is not None:
        return
    vault = VaultManager()
    try:
        info = vault.vault_info()
        if not info.get("initialized"):
            console.print("  [bold #D39CE0]Vault not initialized.[/bold #D39CE0]")
            console.print("  [dim]Run '[bold #9C27B0]aegis setup[/bold #9C27B0]' to create your vault[/dim]")
        elif not info.get("authenticated"):
            console.print("  [bold #FFC107][WARN][/bold #FFC107] Not authenticated")
            console.print("  [dim]Run '[bold #9C27B0]aegis auth[/bold #9C27B0]' to authenticate[/dim]")
        else:
            console.print(f"  [bold #4CAF50][OK][/bold #4CAF50] Authenticated [dim]({info.get('secret_count', 0)} secrets)[/dim]")
            console.print("  [dim]Commands: save, show, list, delete, find, generate, lock[/dim]")
    except Exception:
        pass


# Import commands
from cli.commands.setup import setup
from cli.commands.auth import auth
from cli.commands.save import save
from cli.commands.show import show
from cli.commands.list import list_secrets
from cli.commands.delete import delete
from cli.commands.generate import generate
from cli.commands.find import find
from cli.commands.lock import lock

cli.add_command(setup)
cli.add_command(auth)
cli.add_command(save)
cli.add_command(show)
cli.add_command(list_secrets)
cli.add_command(delete)
cli.add_command(generate)
cli.add_command(find)
cli.add_command(lock)


if __name__ == "__main__":
    cli()
