import click
from click import Group
from cli.utils.output import console, print_header


def display_main_help():
    """Display main help with ASCII art and command list."""
    print_header()

    lines = [
        "",
        "Commands:",
        "  save              Save a secret: aegis save NAME VALUE TAG",
        "  show              Get a secret: aegis show NAME",
        "  list              List secrets: aegis list [TAG]",
        "  find              Search: aegis find QUERY",
        "  delete            Delete: aegis delete NAME",
        "  generate          Generate password: aegis generate [LENGTH]",
        "  auth              Authenticate: aegis auth",
        "  lock              Lock vault: aegis lock",
        "",
        "Examples:",
        "  aegis save github-token ghp_1234567890 password",
        "  aegis show github-token",
        "  aegis list password",
        "  aegis find database",
        "  aegis delete old-key",
        "  aegis generate 32",
        "  aegis auth",
        "  aegis lock",
        "",
        "Run 'aegis COMMAND --help' for more info on a command.",
    ]

    for line in lines:
        if line.startswith("Commands:") or line.startswith("Examples:"):
            console.print(f"  [bold #D39CE0]{line}[/bold #D39CE0]")
        elif line.strip() == "":
            console.print()
        else:
            console.print(f"  {line}")


class AegisGroup(Group):
    """Custom group that shows our help instead of Click's default."""

    def get_help(self, ctx):
        display_main_help()
        return ""


@click.group(cls=AegisGroup, invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Aegis v1.0.0 - Encrypted Secrets Manager"""
    if ctx.invoked_subcommand is not None:
        return
    display_main_help()


@cli.command(name="help")
@click.pass_context
def help_cmd(ctx):
    """Show help and exit."""
    display_main_help()


# Import commands
from cli.commands.auth import auth
from cli.commands.save import save
from cli.commands.show import show
from cli.commands.list import list_cmd
from cli.commands.delete import delete
from cli.commands.find import find
from cli.commands.generate import generate
from cli.commands.lock import lock

cli.add_command(auth)
cli.add_command(save)
cli.add_command(show)
cli.add_command(list_cmd, name="list")
cli.add_command(delete)
cli.add_command(find)
cli.add_command(generate)
cli.add_command(lock)


if __name__ == "__main__":
    cli()
