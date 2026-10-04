#!/usr/bin/env python3
"""Tally severity-bearing Markdown headings; this is not factual verification."""
import argparse
import collections
from pathlib import Path
import re

UNCONFIRMED = re.compile(r"unconfirmed|to be confirmed", re.I)
VOCABULARIES = {"standard": ("BLOCKER", "MAJOR", "MINOR"),
                "high-medium": ("BLOCKER", "HIGH", "MEDIUM")}


def tally(text, vocabulary="standard"):
    severity = re.compile(r"\b(" + "|".join(VOCABULARIES[vocabulary]) + r")\b")
    counts, unconfirmed = collections.Counter(), 0
    for line in text.splitlines():
        if not line.startswith("#"):
            continue
        match = severity.search(line)
        if match:
            if UNCONFIRMED.search(line):
                unconfirmed += 1
            else:
                counts[match.group(1)] += 1
    return counts, unconfirmed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vocabulary", choices=VOCABULARIES, default="standard")
    parser.add_argument("reports", nargs="+")
    args = parser.parse_args()
    labels = VOCABULARIES[args.vocabulary]
    print("\t".join(("round", *labels, "unconfirmed", "file")))
    for round_number, path in enumerate(args.reports, 1):
        counts, unconfirmed = tally(Path(path).read_text(), args.vocabulary)
        print("\t".join(map(str, (round_number, *(counts[label] for label in labels),
                                    unconfirmed, Path(path).name))))


if __name__ == "__main__":
    main()
