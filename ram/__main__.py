"""python -m ram < noting.txt
For each act in the noting: "<doer> karega" when a doer that counts is named, "RAM bharose" when none is."""
import os, sys
from .acts import acts
from .kind import counts, short
from .read import Reader

READER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runs", "ram-0.5")
THRESHOLD = 0.0  # 0.5, 15 October 2026: see README; at 0 every doerless act a pointing slipped through was refused by kind.py


def say(noting, reader, threshold=THRESHOLD):
    lines = []
    for _, act, question, end in acts(noting):
        doer, margin = reader.read(question, noting, end)
        if doer and margin > threshold and counts(doer):
            lines.append((act, f"{short(doer)} karega"))
        else:
            lines.append((act, "RAM bharose"))
    return lines


if __name__ == "__main__":
    for act, answer in say(sys.stdin.read(), Reader(READER)):
        print(f"{act:<40} {answer}")
