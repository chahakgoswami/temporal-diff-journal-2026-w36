import argparse
import sys

from tdj.commands.new import cmd_new
from tdj.commands.show import cmd_show
from tdj.commands.diff import cmd_diff


def build_parser():
    parser = argparse.ArgumentParser(
        prog="tdj",
        description="Temporal Diff Journal – a CLI journal that shows how your writing evolves.",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="<command>")

    # ── new ──────────────────────────────────────────────────────────────────────────
    new_parser = subparsers.add_parser(
        "new",
        help="Create a new journal entry for today (or a specified date).",
    )
    new_parser.add_argument(
        "--date",
        metavar="YYYY-MM-DD",
        default=None,
        help="Date for the entry (default: today).",
    )
    new_parser.add_argument(
        "--message", "-m",
        metavar="TEXT",
        default=None,
        help="Entry text (if omitted, opens $EDITOR or prompts for input).",
    )

    # ── show ─────────────────────────────────────────────────────────────────────────
    show_parser = subparsers.add_parser(
        "show",
        help="Display a journal entry by date, 'today', or 'yesterday'.",
    )
    show_parser.add_argument(
        "date",
        metavar="DATE",
        nargs="?",
        default="today",
        help="Date to show: YYYY-MM-DD, 'today' (default), or 'yesterday'.",
    )

    # ── diff ─────────────────────────────────────────────────────────────────────────
    diff_parser = subparsers.add_parser(
        "diff",
        help="Show a word-level diff between two journal entries.",
    )
    diff_parser.add_argument(
        "date_a",
        metavar="DATE_A",
        help="Older entry date: YYYY-MM-DD, 'today', or 'yesterday'.",
    )
    diff_parser.add_argument(
        "date_b",
        metavar="DATE_B",
        help="Newer entry date: YYYY-MM-DD, 'today', or 'yesterday'.",
    )

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "new":
        cmd_new(args)
    elif args.command == "show":
        cmd_show(args)
    elif args.command == "diff":
        cmd_diff(args)
    else:
        parser.print_help()
        sys.exit(1)
