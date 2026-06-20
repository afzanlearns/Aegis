import click
from cli.utils.output import (
    console, print_vault_panel, print_audit_logs, print_error, print_info,
)
from core.vault import VaultManager
from exceptions import AuthenticationError


@click.command()
@click.option("--limit", "-l", default=50, type=int, show_default=True, help="Number of log entries")
def audit(limit):
    """View audit log of all vault operations."""
    vault = VaultManager()

    try:
        logs = vault.get_audit_logs(limit=limit)

        if logs:
            print_vault_panel(
                "audit",
                f"\n  [bold #D39CE0]📋 Audit Log (last {len(logs)} entries)[/bold #D39CE0]\n",
            )
            print_audit_logs(logs)
        else:
            print_info("No audit log entries yet.")
    except AuthenticationError as e:
        print_error(str(e))
        print_info("Run 'aegis auth' first")
        raise SystemExit(1)
