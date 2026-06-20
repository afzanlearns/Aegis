import sys
import click
from cli.utils.output import console, print_vault_panel, print_success, print_error
from core.vault import VaultManager
from exceptions import AuthenticationError


@click.command()
@click.argument("name")
@click.option("--value", "-v", help="Secret value (omit for hidden prompt)")
@click.option("--type", "-t", "secret_type", default="password",
              help="Secret type (password, api-key, duo, url, secret)")
@click.option("--password", "-p", is_flag=True, help="Prompt for hidden value")
def save(name, value, secret_type, password):
    """Save an encrypted secret."""
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
        if password or not value:
            from getpass import getpass
            console.print(f"  [bold #D39CE0]Value for '{name}':[/bold #D39CE0]")
            value = getpass("  ")

        if not value:
            print_error("Value cannot be empty")
            raise SystemExit(1)

        vault.save_secret(name, value, secret_type)
        print_success(f"Saved '{name}'")
    except AuthenticationError as e:
        print_error(str(e))
        print_error("Run 'aegis auth' first")
        raise SystemExit(1)
    except (ValueError, Exception) as e:
        print_error(str(e))
        raise SystemExit(1)
