import sys
from datetime import date, timedelta

from colorama import Fore, Style, init as colorama_init

from tdj.commands.new import entry_path, parse_date

colorama_init(autoreset=True)


def resolve_date(date_str: str) -> date:
    """Resolve a date string (YYYY-MM-DD, 'today', 'yesterday') to a date object."""
    if date_str.lower() == "today":
        return date.today()
    elif date_str.lower() == "yesterday":
        return date.today() - timedelta(days=1)
    else:
        return parse_date(date_str)


def cmd_show(args) -> None:
    """Handle the `tdj show` subcommand."""
    entry_date = resolve_date(args.date)
    path = entry_path(entry_date)

    if not path.exists():
        print(
            Fore.RED + f"No entry found for {entry_date.isoformat()}.",
            file=sys.stderr,
        )
        sys.exit(1)

    content = path.read_text(encoding="utf-8")

    # Header
    print(Fore.CYAN + Style.BRIGHT + f"=== Journal Entry: {entry_date.isoformat()} ===")
    print(Fore.CYAN + "-" * 44)

    # Body – print each line with gentle yellow tint
    for line in content.splitlines():
        if line.strip() == "":
            print()
        else:
            print(Fore.YELLOW + line)

    # Footer
    word_count = len(content.split())
    print(Fore.CYAN + "-" * 44)
    print(Fore.GREEN + f"Word count: {word_count}")
