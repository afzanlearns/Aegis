import sys
import click
from pathlib import Path
from cli.utils.output import console, print_vault_panel, print_success, print_error, print_info
from core.vault import VaultManager
from exceptions import AuthenticationError, ExportError


@click.command()
@click.argument("path")
@click.option("--password", "-pw", help="Export password if backup is encrypted")
def import_cmd(path, password):
    """Import secrets from an encrypted backup file."""
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

    import_path = Path(path).expanduser().resolve()

    try:
        count = vault.import_backup(import_path, export_password=password or None)
        print_success(f"Imported {count} secrets from {import_path}")
    except AuthenticationError as e:
        print_error(str(e))
        print_info("Run 'aegis auth' first")
        raise SystemExit(1)
    except ExportError as e:
        print_error(str(e))
        raise SystemExit(1)
    except Exception as e:
        print_error(f"Import failed: {e}")
        raise SystemExit(1)
