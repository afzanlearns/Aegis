import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from datetime import datetime
from typing import Optional, Dict, List

# Configure console for Windows terminal compatibility
console = Console(
    legacy_windows=False,
    force_terminal=sys.stdout.isatty(),
    color_system="auto",
)

# Purple/gold theme colors
PURPLE = "#9C27B0"
MEDIUM_PURPLE = "#BA68C8"
LIGHT_PURPLE = "#D39CE0"
GOLD = "#FFD700"
SUCCESS = "#4CAF50"
ERROR = "#FF5252"
WARNING = "#FFC107"
NEUTRAL = "#E0E0E0"
BACKGROUND = "#1A1A1A"
TEXT = "#FFFFFF"
MUTED = "#808080"


def print_header() -> None:
    """Print the Aegis ASCII art header."""
    ascii_art = """
    [bold #9C27B0] _    ____  ___    _     _____ [/bold #9C27B0]
    [bold #9C27B0]/ \\  |  _ \\/ _ \\  / |   / ____|[/bold #9C27B0]
    [bold #BA68C8]/ _ \\ | |_) | | | | |   | (___  [/bold #BA68C8]
    [bold #D39CE0]/ ___ \\|  _ <| |_| | |    \\___ \\ [/bold #D39CE0]
    [bold #E0E0E0]/_/   \\_\\_| \\_\\\\___/  |_|    ____) |[/bold #E0E0E0]
    [bold #E0E0E0]                                 |___/ [/bold #E0E0E0]

    [bold #FFD700]Aegis v1.0.0[/bold #FFD700] [dim]- Encrypted Secrets Manager[/dim]
    [italic #808080]"Guardian of Your Credentials"[/italic #808080]
    """
    console.print(ascii_art)


def print_vault_panel(title: str, content: str, border_color: str = PURPLE) -> None:
    """Print content inside a styled panel."""
    panel = Panel(
        Text(content, style=TEXT),
        title=f"[bold {border_color}] {title}[/bold {border_color}]",
        border_style=border_color,
        box=box.ROUNDED,
        padding=(1, 2),
    )
    console.print(panel)


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"  [bold {SUCCESS}][/bold {SUCCESS}] [bold]{message}[/bold]")


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"  [bold {ERROR}][/bold {ERROR}] [bold]{message}[/bold]")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"  [bold {WARNING}][/bold {WARNING}] {message}")


def print_info(message: str) -> None:
    """Print an info message."""
    console.print(f"  [bold {LIGHT_PURPLE}][/bold {LIGHT_PURPLE}] {message}")


def print_secret_list(secrets: List[Dict]) -> None:
    """Print secrets in a formatted table."""
    if not secrets:
        print_info("No secrets stored yet.")
        return

    table = Table(
        box=box.ROUNDED,
        border_style=PURPLE,
        header_style=f"bold {GOLD}",
        padding=(0, 1),
    )
    table.add_column("Name", style=TEXT)
    table.add_column("Type", style=LIGHT_PURPLE)
    table.add_column("Created", style=MUTED)

    for secret in secrets:
        created = secret.get("created", "")
        if created:
            try:
                dt = datetime.fromisoformat(created)
                days_ago = (datetime.now() - dt).days
                if days_ago == 0:
                    created_str = "today"
                elif days_ago == 1:
                    created_str = "1d ago"
                else:
                    created_str = f"{days_ago}d ago"
            except (ValueError, TypeError):
                created_str = created
        else:
            created_str = ""

        name_text = f"  {secret['name']}"
        secret_type = secret.get("type", "password")

        table.add_row(name_text, secret_type, created_str)

    console.print(table)


def print_secret_detail(name: str, value: Optional[str] = None, copied: bool = False) -> None:
    """Print a single secret detail."""
    if value:
        print_success(f"Retrieved '{name}'")
    if copied:
        print_warning("Copied to clipboard - clears in 30s")
        print_info("Tip: Value will auto-clear from clipboard for security")


def print_auth_status(authenticated: bool, expires_in: Optional[int] = None) -> None:
    """Print authentication status."""
    if authenticated:
        if expires_in:
            minutes = expires_in // 60
            seconds = expires_in % 60
            print_success(f"Authenticated (expires in {minutes}m {seconds}s)")
        else:
            print_success("Authenticated")
    else:
        print_warning("Not authenticated")


def print_vault_info(info: Dict) -> None:
    """Print vault information."""
    if not info.get("initialized"):
        print_vault_panel(
            "vault",
            "  Vault not initialized.\n\n  Run 'aegis setup' to create your vault.",
            border_color=WARNING,
        )
        return

    content_lines = []
    if info.get("authenticated"):
        expires = info.get("session_expires_in", 0)
        mins, secs = divmod(expires, 60)
        content_lines.append(f"  [bold {SUCCESS}][/bold {SUCCESS}] Authenticated (expires in {mins}m {secs}s)")
    else:
        content_lines.append(f"  [bold {WARNING}][/bold {WARNING}] Not authenticated")

    content_lines.append("")
    secret_count = info.get("secret_count", 0)
    content_lines.append(f"  Stored Secrets: [bold]{secret_count}[/bold] items")

    if info.get("initialized_at"):
        content_lines.append(f"  [dim]Initialized: {info['initialized_at']}[/dim]")

    content_lines.append("")
    content_lines.append(f"  [dim]Run 'aegis --help' for available commands[/dim]")

    print_vault_panel("vault - status", "\n".join(content_lines))


def print_audit_logs(logs: List[Dict]) -> None:
    """Print audit log entries."""
    if not logs:
        print_info("No audit log entries.")
        return

    table = Table(
        box=box.ROUNDED,
        border_style=PURPLE,
        header_style=f"bold {GOLD}",
        padding=(0, 1),
    )
    table.add_column("Time", style=MUTED)
    table.add_column("Action", style=TEXT)
    table.add_column("Secret", style=LIGHT_PURPLE)
    table.add_column("Status", style=TEXT)

    for log in logs:
        ts = log.get("timestamp", "")
        if ts:
            try:
                dt = datetime.fromisoformat(ts)
                ts = dt.strftime("%H:%M:%S")
            except (ValueError, TypeError):
                pass

        action = log.get("action", "")
        secret = log.get("secret_name", "") or "-"
        success = log.get("success", True)
        status = f"[bold {SUCCESS}][/bold {SUCCESS}]" if success else f"[bold {ERROR}][/bold {ERROR}]"

        table.add_row(ts, action, secret, status)

    console.print(table)


def prompt_master_password(confirm: bool = False) -> str:
    """Prompt for master password with hidden input."""
    from getpass import getpass

    while True:
        password = getpass("  Master Password: ")
        if len(password) < 12:
            print_error("Password must be at least 12 characters")
            continue

        strength = _password_strength_label(password)
        if "Weak" in strength:
            print_warning(f"Password strength: {strength}")
            try:
                proceed = input("  Continue anyway? [y/N] ").lower().strip()
                if proceed != "y":
                    continue
            except (EOFError, KeyboardInterrupt):
                raise
        else:
            print_success(f"Password strength: {strength}")

        if confirm:
            confirm_password = getpass("  Confirm Master Password: ")
            if password != confirm_password:
                print_error("Passwords do not match")
                continue

        return password


def _password_strength_label(password: str) -> str:
    """Return a human-readable strength label."""
    length_score = min(len(password) // 4, 4)
    types = 0
    if any(c.islower() for c in password):
        types += 1
    if any(c.isupper() for c in password):
        types += 1
    if any(c.isdigit() for c in password):
        types += 1
    if any(c in "!@#$%^&*()_+-=[]{}|:;<>?,./" for c in password):
        types += 1

    total = length_score + types
    if total >= 7:
        return "Very Strong"
    elif total >= 5:
        return "Strong"
    elif total >= 3:
        return "Moderate"
    else:
        return "Weak"
