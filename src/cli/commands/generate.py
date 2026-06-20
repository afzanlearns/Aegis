import click
from cli.utils.output import console, print_vault_panel, print_success, print_info
from core.vault import VaultManager


@click.command()
@click.option("--length", "-l", default=32, type=int, show_default=True, help="Password length")
@click.option("--no-symbols", is_flag=True, help="Exclude symbols")
@click.option("--save", "-s", help="Save generated password with this name")
@click.option("--type", "-t", "secret_type", default="password", help="Secret type when saving")
def generate(length, no_symbols, save, secret_type):
    """Generate a strong random password."""
    vault = VaultManager()

    password = vault.generate_password(length=length, symbols=not no_symbols)

    print_vault_panel(
        "generate",
        f"\n  [bold #D39CE0]🔑 Generated Password[/bold #D39CE0]\n\n"
        f"  [bold #FFFFFF]{password}[/bold #FFFFFF]\n\n"
        f"  [dim]Length: {length} | Symbols: {'Yes' if not no_symbols else 'No'}[/dim]",
    )

    if save:
        try:
            vault.save_secret(save, password, secret_type)
            print_success(f"Saved as '{save}'")
        except Exception as e:
            from cli.utils.output import print_error
            print_error(f"Failed to save: {e}")
