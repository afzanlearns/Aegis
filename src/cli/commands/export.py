import click
from pathlib import Path
from cli.utils.output import console, print_vault_panel, print_success, print_error, print_info, print_warning
from core.vault import VaultManager
from exceptions import AuthenticationError


@click.command()
@click.option("--path", "-p", default="~/aegis-backup.json", help="Output path for backup")
@click.option("--password", "-pw", help="Optional export password for extra encryption")
def export(path, password):
    """Export all secrets as an encrypted JSON backup."""
    vault = VaultManager()
    export_path = Path(path).expanduser().resolve()

    try:
        vault.export_backup(export_path, export_password=password or None)
        print_success(f"Exported to {export_path}")
        if password:
            print_info("Backup is password-encrypted")
        else:
            print_warning("Backup contains plaintext secrets — keep it safe!")
    except AuthenticationError as e:
        print_error(str(e))
        print_info("Run 'aegis auth' first")
        raise SystemExit(1)
    except Exception as e:
        print_error(f"Export failed: {e}")
        raise SystemExit(1)
