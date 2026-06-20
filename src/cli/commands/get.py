import click
from cli.utils.output import (
    console, print_vault_panel, print_success, print_error,
    print_info, print_warning,
)
from core.vault import VaultManager
from exceptions import AuthenticationError, SecretNotFoundError, DecryptionError


@click.command()
@click.argument("name")
@click.option("--copy", "-c", is_flag=True, help="Copy to clipboard (clears in 30s)")
def get(name, copy):
    """Retrieve a decrypted secret."""
    vault = VaultManager()

    try:
        value = vault.get_secret(name, copy=copy)

        if copy:
            print_vault_panel(
                f"get {name}",
                f"\n  [bold #4CAF50]✓[/bold #4CAF50] Retrieved '{name}'\n"
                f"  [bold #FFC107]📋[/bold #FFC107] Copied to clipboard (clears in 30s)\n\n"
                f"  [dim]💡 Value will auto-clear from clipboard for security[/dim]",
            )
        else:
            print_vault_panel(
                f"get {name}",
                f"\n  [bold #4CAF50]✓[/bold #4CAF50] Retrieved '{name}'\n\n"
                f"  [bold #FFFFFF]{value}[/bold #FFFFFF]\n",
            )
    except AuthenticationError as e:
        print_error(str(e))
        print_info("Run 'aegis auth' first")
        raise SystemExit(1)
    except (SecretNotFoundError, DecryptionError) as e:
        print_error(str(e))
        raise SystemExit(1)
