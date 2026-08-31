import os
import subprocess
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path

JOURNAL_DIR = Path.home() / ".tdj"


def get_journal_dir() -> Path:
    """Return (and create if needed) the journal storage directory."""
    JOURNAL_DIR.mkdir(parents=True, exist_ok=True)
    return JOURNAL_DIR


def parse_date(date_str: str) -> date:
    """Parse a YYYY-MM-DD string into a date object."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        print(f"Error: '{date_str}' is not a valid date (expected YYYY-MM-DD).", file=sys.stderr)
        sys.exit(1)


def entry_path(entry_date: date) -> Path:
    """Return the file path for a given entry date."""
    return get_journal_dir() / f"{entry_date.isoformat()}.txt"


def open_in_editor(path: Path) -> None:
    """Open *path* in the user's preferred editor."""
    editor = os.environ.get("VISUAL") or os.environ.get("EDITOR") or "nano"
    subprocess.call([editor, str(path)])


def prompt_for_text() -> str:
    """Prompt the user to type their entry interactively, ending with EOF (Ctrl-D)."""
    print("Enter your journal entry (press Ctrl-D on a new line when done):")
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    return "\n".join(lines)


def cmd_new(args) -> None:
    """Handle the `tdj new` subcommand."""
    # Determine entry date
    entry_date = parse_date(args.date) if args.date else date.today()
    path = entry_path(entry_date)

    already_exists = path.exists()

    if args.message:
        # Non-interactive: append (or create) with the supplied message
        with path.open("a", encoding="utf-8") as fh:
            if already_exists and path.stat().st_size > 0:
                fh.write("\n")  # separate from previous content
            fh.write(args.message)
            if not args.message.endswith("\n"):
                fh.write("\n")
        action = "Updated" if already_exists else "Created"
        print(f"{action} entry: {path}")
    elif sys.stdin.isatty():
        # Interactive terminal: open editor
        if not already_exists:
            # Write an empty file so the editor opens a clean slate
            path.touch()
        open_in_editor(path)
        print(f"Entry saved: {path}")
    else:
        # Piped input (e.g. echo '...' | tdj new)
        text = sys.stdin.read()
        with path.open("a", encoding="utf-8") as fh:
            if already_exists and path.stat().st_size > 0:
                fh.write("\n")
            fh.write(text)
        action = "Updated" if already_exists else "Created"
        print(f"{action} entry: {path}")
