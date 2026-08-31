# Temporal Diff Journal

A CLI journal that shows how your writing has evolved over time using smart diffs.

**Language:** python

## 7-day build plan

- [ ] Day 1: Set up the project with a CLI entry point using argparse; implement `new` command that creates dated plaintext entries stored in ~/.tdj/YYYY-MM-DD.txt.
- [ ] Day 2: Implement `show` command to display a single entry by date or keyword 'today'/'yesterday', with colorized output using colorama.
- [ ] Day 3: Implement `diff` command that computes and pretty-prints a word-level diff between any two dated entries using Python's difflib.
- [ ] Day 4: Add `log` command that lists all entry dates with a one-line summary (first sentence) and word count for each entry.
- [ ] Day 5: Add `evolve` command that chains diffs across all entries chronologically, highlighting which phrases recur, grow, or disappear over time.
- [ ] Day 6: Implement `search` command with substring and regex support that shows matching lines across all entries with their dates highlighted.
- [ ] Day 7: Add `stats` command that renders a small ASCII chart of word-count-per-day over time, and package the project with a pyproject.toml for pip install.

---
_Built and deployed by Chahak Goswami._
