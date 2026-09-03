import sys
from difflib import SequenceMatcher

from colorama import Fore, Style, init as colorama_init

from tdj.commands.new import entry_path
from tdj.commands.show import resolve_date

colorama_init(autoreset=True)


def tokenize(text: str) -> list:
    """Split text into a list of tokens (words and whitespace/punctuation)."""
    import re
    # Split keeping whitespace as separate tokens so we can reconstruct output
    return re.split(r'(\s+)', text)


def word_diff(old_text: str, new_text: str) -> str:
    """Compute a word-level diff and return a colorized string."""
    old_tokens = tokenize(old_text)
    new_tokens = tokenize(new_text)

    matcher = SequenceMatcher(None, old_tokens, new_tokens, autojunk=False)
    output_parts = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        old_chunk = "".join(old_tokens[i1:i2])
        new_chunk = "".join(new_tokens[j1:j2])

        if tag == "equal":
            output_parts.append(Style.RESET_ALL + old_chunk)
        elif tag == "replace":
            output_parts.append(Fore.RED + Style.BRIGHT + old_chunk + Style.RESET_ALL)
            output_parts.append(Fore.GREEN + Style.BRIGHT + new_chunk + Style.RESET_ALL)
        elif tag == "delete":
            output_parts.append(Fore.RED + Style.BRIGHT + old_chunk + Style.RESET_ALL)
        elif tag == "insert":
            output_parts.append(Fore.GREEN + Style.BRIGHT + new_chunk + Style.RESET_ALL)

    return "".join(output_parts)


def cmd_diff(args) -> None:
    """Handle the `tdj diff` subcommand."""
    date_a = resolve_date(args.date_a)
    date_b = resolve_date(args.date_b)

    path_a = entry_path(date_a)
    path_b = entry_path(date_b)

    missing = []
    if not path_a.exists():
        missing.append(date_a.isoformat())
    if not path_b.exists():
        missing.append(date_b.isoformat())

    if missing:
        for d in missing:
            print(Fore.RED + f"No entry found for {d}.", file=sys.stderr)
        sys.exit(1)

    text_a = path_a.read_text(encoding="utf-8")
    text_b = path_b.read_text(encoding="utf-8")

    # Header
    print(Fore.CYAN + Style.BRIGHT + f"=== Diff: {date_a.isoformat()}  →  {date_b.isoformat()} ===")
    print(Fore.RED + Style.BRIGHT + "[-removed-]  " + Fore.GREEN + Style.BRIGHT + "[+added+]")
    print(Fore.CYAN + "-" * 50)

    if text_a == text_b:
        print(Fore.YELLOW + "(Entries are identical – no differences found.)")
    else:
        diff_output = word_diff(text_a, text_b)
        print(diff_output)

    print(Fore.CYAN + "-" * 50)

    wc_a = len(text_a.split())
    wc_b = len(text_b.split())
    delta = wc_b - wc_a
    sign = "+" if delta >= 0 else ""
    print(
        Fore.GREEN
        + f"Words: {date_a.isoformat()} = {wc_a}  |  {date_b.isoformat()} = {wc_b}  "
        + f"(delta: {sign}{delta})"
    )
