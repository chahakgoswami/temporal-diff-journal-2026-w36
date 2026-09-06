import re
import sys
from collections import Counter
from difflib import SequenceMatcher

from colorama import Fore, Style, init as colorama_init

from tdj.commands.new import get_journal_dir

colorama_init(autoreset=True)


def tokenize_words(text: str) -> list:
    """Return a list of lowercase words (no punctuation) from text."""
    return re.findall(r"[a-zA-Z']+", text.lower())


def extract_phrases(text: str, n: int = 3) -> Counter:
    """Extract n-gram phrases (default trigrams) from text and count them."""
    words = tokenize_words(text)
    phrases = Counter()
    for i in range(len(words) - n + 1):
        phrase = " ".join(words[i:i + n])
        phrases[phrase] += 1
    return phrases


def word_level_tokens(text: str) -> list:
    """Split text into word + whitespace tokens for diff computation."""
    return re.split(r'(\s+)', text)


def colorized_word_diff(old_text: str, new_text: str) -> str:
    """Return a colorized word-level diff string between two texts."""
    old_tokens = word_level_tokens(old_text)
    new_tokens = word_level_tokens(new_text)

    matcher = SequenceMatcher(None, old_tokens, new_tokens, autojunk=False)
    parts = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        old_chunk = "".join(old_tokens[i1:i2])
        new_chunk = "".join(new_tokens[j1:j2])

        if tag == "equal":
            parts.append(Style.RESET_ALL + old_chunk)
        elif tag == "replace":
            parts.append(Fore.RED + Style.BRIGHT + old_chunk + Style.RESET_ALL)
            parts.append(Fore.GREEN + Style.BRIGHT + new_chunk + Style.RESET_ALL)
        elif tag == "delete":
            parts.append(Fore.RED + Style.BRIGHT + old_chunk + Style.RESET_ALL)
        elif tag == "insert":
            parts.append(Fore.GREEN + Style.BRIGHT + new_chunk + Style.RESET_ALL)

    return "".join(parts)


def analyse_phrase_evolution(texts_by_date: list) -> dict:
    """
    Given a list of (date_str, text) pairs (chronological), compute:
      - recurring: phrases present in 3+ entries
      - grown:     phrases whose count increased entry-to-entry on average
      - vanished:  phrases present only in earlier half but not later half
    Returns a dict with sets/lists for each category.
    """
    n = 3  # trigram size
    counters = [(ds, extract_phrases(txt, n)) for ds, txt in texts_by_date]

    # Collect all phrases
    all_phrases = set()
    for _, counter in counters:
        all_phrases.update(counter.keys())

    recurring = set()
    grown = set()
    vanished = set()

    total = len(counters)
    half = max(1, total // 2)

    for phrase in all_phrases:
        presence = [c[phrase] for _, c in counters]  # count per entry (0 if absent)
        entries_present = sum(1 for p in presence if p > 0)

        # Recurring: appears in 3 or more entries
        if entries_present >= 3:
            recurring.add(phrase)

        # Grown: count in later half > count in earlier half
        early_count = sum(presence[:half])
        late_count = sum(presence[half:])
        if late_count > early_count and late_count > 0:
            grown.add(phrase)

        # Vanished: present in first half, absent from second half
        early_present = any(p > 0 for p in presence[:half])
        late_present = any(p > 0 for p in presence[half:])
        if early_present and not late_present:
            vanished.add(phrase)

    return {"recurring": recurring, "grown": grown, "vanished": vanished}


def cmd_evolve(args) -> None:
    """Handle the `tdj evolve` subcommand."""
    journal_dir = get_journal_dir()
    entries = sorted(journal_dir.glob("[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].txt"))

    if len(entries) < 2:
        print(
            Fore.YELLOW + "Need at least 2 journal entries to show evolution.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Load all entries
    texts_by_date = []
    for path in entries:
        date_str = path.stem
        content = path.read_text(encoding="utf-8")
        texts_by_date.append((date_str, content))

    # ── Chained word-level diffs ──────────────────────────────────────────────
    print(Fore.CYAN + Style.BRIGHT + "=" * 60)
    print(Fore.CYAN + Style.BRIGHT + "  TEMPORAL EVOLUTION – Chained Entry Diffs")
    print(Fore.CYAN + Style.BRIGHT + "=" * 60)
    print(
        Fore.RED + Style.BRIGHT + "[-removed-]  "
        + Fore.GREEN + Style.BRIGHT + "[+added+]"
        + Style.RESET_ALL
    )
    print()

    for i in range(len(texts_by_date) - 1):
        date_a, text_a = texts_by_date[i]
        date_b, text_b = texts_by_date[i + 1]

        print(Fore.CYAN + "-" * 60)
        print(
            Fore.CYAN + Style.BRIGHT
            + f"  {date_a}  →  {date_b}"
            + Style.RESET_ALL
        )
        print(Fore.CYAN + "-" * 60)

        if text_a.strip() == text_b.strip():
            print(Fore.YELLOW + "  (Entries are identical – no differences.)")
        else:
            diff_output = colorized_word_diff(text_a, text_b)
            print(diff_output)

        wc_a = len(text_a.split())
        wc_b = len(text_b.split())
        delta = wc_b - wc_a
        sign = "+" if delta >= 0 else ""
        print(
            "\n" + Fore.MAGENTA
            + f"  Words: {date_a}={wc_a}  {date_b}={wc_b}  (delta: {sign}{delta})"
            + Style.RESET_ALL
        )
        print()

    # ── Phrase-level insights (only when 2+ entries available for n-grams) ────
    if len(texts_by_date) >= 2:
        print(Fore.CYAN + "=" * 60)
        print(Fore.CYAN + Style.BRIGHT + "  PHRASE INSIGHTS (trigrams across all entries)")
        print(Fore.CYAN + "=" * 60)

        insights = analyse_phrase_evolution(texts_by_date)

        # Recurring
        print(Fore.GREEN + Style.BRIGHT + "\nRecurring phrases (3+ entries):")
        if insights["recurring"]:
            for phrase in sorted(insights["recurring"])[:15]:  # cap at 15
                print(Fore.GREEN + f"  • {phrase}")
        else:
            print(Fore.WHITE + "  (none found)")

        # Grown
        print(Fore.YELLOW + Style.BRIGHT + "\nGrowing phrases (more common over time):")
        # Exclude phrases already listed as recurring to reduce overlap
        grown_unique = insights["grown"] - insights["recurring"]
        if grown_unique:
            for phrase in sorted(grown_unique)[:15]:
                print(Fore.YELLOW + f"  ↑ {phrase}")
        else:
            print(Fore.WHITE + "  (none found)")

        # Vanished
        print(Fore.RED + Style.BRIGHT + "\nVanished phrases (dropped from later entries):")
        if insights["vanished"]:
            for phrase in sorted(insights["vanished"])[:15]:
                print(Fore.RED + f"  ✕ {phrase}")
        else:
            print(Fore.WHITE + "  (none found)")

        print()
        print(Fore.CYAN + "=" * 60)
