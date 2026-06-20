import sys
import click
from cli.utils.output import (
    console, print_vault_panel, print_secret_list, print_error, print_info,
)
from core.vault import VaultManager
from exceptions import AuthenticationError


@click.command()
@click.argument("query")
def search(query):
    """Search secrets by name."""
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
        results = vault.search_secrets(query)

        if results:
            print_vault_panel(
                "search",
                f"\n  [bold #D39CE0]🔍 Search results for '{query}' ({len(results)} found)[/bold #D39CE0]\n",
            )
            print_secret_list(results)
        else:
            print_info(f"No secrets matching '{query}'")
    except AuthenticationError as e:
        print_error(str(e))
        print_info("Run 'aegis auth' first")
        raise SystemExit(1)
