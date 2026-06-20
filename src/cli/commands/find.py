import sys
import click
from cli.utils.output import console, print_secret_list
from core.vault import VaultManager


@click.command()
@click.argument("query")
def find(query):
    """Search secrets by name.

    Usage: aegis find QUERY

    Examples:

      aegis find github

      aegis find password

      aegis find database
    """
    vault = VaultManager()

    if not vault.is_authenticated():
        console.print("  [bold #FFC107][WARN][/bold #FFC107] Not authenticated")
        console.print("  [dim][*] Run: aegis auth[/dim]")
        sys.exit(1)

    try:
        results = vault.search_secrets(query)

        if results:
            console.print(f"  [bold #D39CE0]Found {len(results)} secret[/bold #D39CE0]")
            print_secret_list(results)
        else:
            console.print(f"  [bold #D39CE0][*][/bold #D39CE0] No secrets matching '{query}'")
    except Exception as e:
        console.print(f"  [bold #FF5252][ERR][/bold #FF5252] {e}")
        sys.exit(1)
