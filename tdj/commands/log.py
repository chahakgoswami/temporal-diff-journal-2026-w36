import re
import sys

from colorama import Fore, Style, init as colorama_init

from tdj.commands.new import get_journal_dir

colorama_init(autoreset=True)


def first_sentence(text: str) -> str:
    """Extract the first sentence from text, falling back to the first non-empty line."""
    # Strip leading whitespace/blank lines
    stripped = text.strip()
    if not stripped:
        return "(empty entry)"

    # Try to find end of first sentence by punctuation
    match = re.search(r'[.!?]', stripped)
    if match:
        sentence = stripped[:match.start() + 1].strip()
        # Replace internal newlines with a space for cleaner display
        sentence = re.sub(r'\s+', ' ', sentence)
        return sentence

    # No sentence-ending punctuation – return first non-empty line
    for line in stripped.splitlines():
        line = line.strip()
        if line:
            # Truncate to 80 chars if needed
            return line[:80] + ("..." if len(line) > 80 else "")

    return "(empty entry)"


def cmd_log(args) -> None:
    """Handle the `tdj log` subcommand."""
    journal_dir = get_journal_dir()
    entries = sorted(journal_dir.glob("[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].txt"))

    if not entries:
        print(Fore.YELLOW + "No journal entries found.")
        return

    # Header
    print(Fore.CYAN + Style.BRIGHT + "=== Journal Log ===")
    print(Fore.CYAN + "-" * 60)

    for path in entries:
        date_str = path.stem  # filename without extension is the date
        content = path.read_text(encoding="utf-8")
        word_count = len(content.split())
        summary = first_sentence(content)

        print(
            Fore.GREEN + Style.BRIGHT + date_str
            + Fore.WHITE + "  "
            + Fore.YELLOW + summary
            + Fore.WHITE + "  "
            + Fore.MAGENTA + f"[{word_count} words]"
        )

    print(Fore.CYAN + "-" * 60)
    print(Fore.GREEN + f"Total entries: {len(entries)}")
