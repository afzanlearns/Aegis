import click
from cli.utils.output import (
    console, print_header, print_vault_info, print_error,
)
from core.vault import VaultManager


@click.group(invoke_without_command=True)
@click.option("--version", "-v", is_flag=True, help="Show version")
@click.pass_context
def cli(ctx, version):
    """Aegis - Encrypted Secrets Manager."""
    if version:
        print_header()
        return

    if ctx.invoked_subcommand is None:
        print_header()
        vault = VaultManager()
        try:
            info = vault.vault_info()
            print_vault_info(info)
        except Exception as e:
            print_error(f"Error reading vault: {e}")


@cli.command()
@click.pass_context
def status(ctx):
    """Show vault status and info."""
    print_header()
    vault = VaultManager()
    try:
        info = vault.vault_info()
        print_vault_info(info)
    except Exception as e:
        print_error(f"Error: {e}")


# Import commands
from cli.commands.setup import setup
from cli.commands.auth import auth
from cli.commands.save import save
from cli.commands.get import get
from cli.commands.list import list_secrets
from cli.commands.delete import delete
from cli.commands.generate import generate
from cli.commands.search import search
from cli.commands.audit import audit
from cli.commands.logout import logout
from cli.commands.export import export
from cli.commands.import_cmd import import_cmd

cli.add_command(setup)
cli.add_command(auth)
cli.add_command(save)
cli.add_command(get)
cli.add_command(list_secrets)
cli.add_command(delete)
cli.add_command(generate)
cli.add_command(search)
cli.add_command(audit)
cli.add_command(logout)
cli.add_command(export)
cli.add_command(import_cmd)


if __name__ == "__main__":
    cli()
