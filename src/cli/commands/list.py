import sys
import click
from cli.utils.output import console, print_secret_list, print_error, print_info
from core.vault import VaultManager


@click.command()
@click.argument("tag", required=False)
def list_secrets(tag):
    """List all secrets or filter by tag."""
    vault = VaultManager()
    if not vault.is_authenticated():
        console.print(
            "[#9C27B0 bold][ERR][/#9C27B0 bold] Not authenticated",
            style="#FF5252"
        )
        console.print(
            "[dim]Run '[#9C27B0]aegis auth[/#9C27B0]' to authenticate[/dim]"
        )
        sys.exit(1)

    try:
        if tag:
            secrets = vault.list_secrets_by_tag(tag)
            if secrets:
                console.print(f"  [bold #D39CE0]{tag.title()}s ({len(secrets)} stored)[/bold #D39CE0]")
            else:
                print_info(f"No secrets tagged '{tag}'")
                return
        else:
            secrets = vault.list_secrets()
            if secrets:
                console.print(f"  [bold #D39CE0]Your Secrets ({len(secrets)} stored)[/bold #D39CE0]")
            else:
                print_info("No secrets stored yet.")
                return

        print_secret_list(secrets)
        if not tag:
            print_info("")
            print_info("[*] Tip: aegis show <name>  or  aegis list <tag>")
    except Exception as e:
        print_error(str(e))
        sys.exit(1)
