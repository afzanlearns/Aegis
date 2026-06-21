import sys
import click
from cli.utils.output import console, print_secret_list, CleanCommand
from core.vault import VaultManager


@click.command(cls=CleanCommand)
@click.argument("tag", required=False)
def list_cmd(tag):
    """List all secrets or filter by tag.

    Arguments:
      TAG               (optional) Filter by tag (password, api, env, etc)

    Examples:
      aegis list                    Show all secrets
      aegis list password           Show only passwords
      aegis list api                Show only API keys
      aegis list env                Show only environment variables
    """
    vault = VaultManager()

    if not vault.is_authenticated():
        console.print("  [bold #FFC107][WARN][/bold #FFC107] Not authenticated")
        console.print("  [dim][*] Run: aegis auth[/dim]")
        sys.exit(1)

    try:
        if tag:
            secrets = vault.list_secrets_by_tag(tag)
            if secrets:
                console.print(f"  [bold #D39CE0]{tag.title()} ({len(secrets)})[/bold #D39CE0]")
            else:
                console.print(f"  [bold #D39CE0][*][/bold #D39CE0] No secrets tagged '{tag}'")
                return
        else:
            secrets = vault.list_secrets()
            if secrets:
                console.print(f"  [bold #D39CE0]Your Secrets ({len(secrets)} stored)[/bold #D39CE0]")
            else:
                console.print("  [bold #D39CE0][*][/bold #D39CE0] No secrets stored yet.")
                return

        print_secret_list(secrets)
    except Exception as e:
        console.print(f"  [bold #FF5252][ERR][/bold #FF5252] {e}")
        sys.exit(1)
