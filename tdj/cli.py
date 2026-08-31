import argparse
import sys

from tdj.commands.new import cmd_new


def build_parser():
    parser = argparse.ArgumentParser(
        prog="tdj",
        description="Temporal Diff Journal – a CLI journal that shows how your writing evolves.",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="<command>")

    # ── new ──────────────────────────────────────────────────────────────────
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

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "new":
        cmd_new(args)
    else:
        parser.print_help()
        sys.exit(1)
