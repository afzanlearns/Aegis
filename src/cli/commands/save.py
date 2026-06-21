import sys
import click
from cli.utils.output import console, CleanCommand
from core.vault import VaultManager


@click.command(cls=CleanCommand)
@click.argument("name")
@click.argument("value")
@click.argument("tag")
def save(name, value, tag):
    """Save a secret with a tag.

    Arguments:
      NAME              Name/identifier for the secret
      VALUE             The secret value (password, token, key, etc)
      TAG               Category tag (password, api, env, database, etc)

    Examples:
      aegis save github-token ghp_1234567890 password
      aegis save database-password MyPass123! password
      aegis save stripe-key sk_live_xxxxx api
      aegis save openai-key sk-proj-xxxxx env
      aegis save prod-db-url postgres://user:pass@host database
    """
    vault = VaultManager()

    if not vault.is_authenticated():
        console.print("  [bold #FFC107][WARN][/bold #FFC107] Not authenticated")
        console.print("  [dim][*] Run: aegis auth[/dim]")
        sys.exit(1)

    if not value:
        console.print("  [bold #FF5252][ERR][/bold #FF5252] Value cannot be empty")
        sys.exit(1)

    try:
        is_update = vault.save_secret(name, value, tag=tag)
        action = "Updated" if is_update else "Saved"
        console.print(f"  [bold #4CAF50][OK][/bold #4CAF50] {action} '[bold]{name}[/bold]' [[bold #D39CE0]{tag}[/bold #D39CE0]]")
    except Exception as e:
        console.print(f"  [bold #FF5252][ERR][/bold #FF5252] {e}")
        sys.exit(1)
