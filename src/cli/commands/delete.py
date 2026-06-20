import sys
import click
from cli.utils.output import console, print_vault_panel, print_success, print_error, print_info
from core.vault import VaultManager
from exceptions import AuthenticationError, SecretNotFoundError


@click.command()
@click.argument("name")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation")
def delete(name, force):
    """Delete a stored secret."""
    vault = VaultManager()
    if not vault.is_authenticated():
        console.print(
            "[#9C27B0 bold]✗ Error:[/#9C27B0 bold] Not authenticated",
            style="#FF5252"
        )
        console.print(
            "[dim]Run '[#9C27B0]aegis auth[/#9C27B0]' first to authenticate[/dim]"
        )
        sys.exit(1)

    try:
        if not force:
            try:
                click.confirm(
                    f"  [bold #FFC107]⚠ Are you sure you want to delete '{name}'?[/bold #FFC107]",
                    abort=True,
                )
            except click.Abort:
                print_info("Cancelled")
                return

        vault.delete_secret(name)
        print_success(f"Deleted '{name}'")
    except AuthenticationError as e:
        print_error(str(e))
        print_info("Run 'aegis auth' first")
        raise SystemExit(1)
    except SecretNotFoundError as e:
        print_error(str(e))
        raise SystemExit(1)
