import sys
import click
from cli.utils.output import console, print_secret_list, print_error, print_info
from core.vault import VaultManager


@click.command()
@click.argument("query")
def find(query):
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
            console.print(f"  [bold #D39CE0]Found {len(results)} secret[/bold #D39CE0]")
            print_secret_list(results)
        else:
            print_info(f"No secrets matching '{query}'")
    except Exception as e:
        print_error(str(e))
        sys.exit(1)
