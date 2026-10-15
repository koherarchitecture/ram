"""A noting longer than the reader takes (384 tokens) is read act by act up to the end of each act's sentence, so no act is lost to the
cut. Puts every test noting after, and before, a long run of references that names nobody and has no acts, and requires each act to
get the same answer as when its noting is read alone: RAM bharose both times, or doers of which one contains the other
("Shri Ramesh Kumar" and "Shri Ramesh Kumar, Assistant"), as tests/measure.py judges. How an act is shown may differ.
usage: python tests/test_long.py [reader]"""
import glob, json, os, re, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from ram.__main__ import say, READER
from ram.read import Reader

reader = Reader(sys.argv[1] if len(sys.argv) > 1 else READER)
norm = lambda t: " ".join(re.sub(r"[^a-z ]", " ", t.lower()).split())


def same(a, b):
    if "RAM bharose" in (a, b):
        return a == b
    a, b = norm(a.removesuffix(" karega")), norm(b.removesuffix(" karega"))
    return a in b or b in a


FILLER = " ".join(f"Reference {i}: earlier notes on page {i}." for i in range(1, 60))
assert say(FILLER, reader) == [], "the filler must have no acts"
notings = [json.loads(l)["noting"] for f in sorted(glob.glob(os.path.join(HERE, "tests", "notings*.jsonl"))) for l in open(f)]
wrong = []
for n in notings:
    alone = say(n, reader)
    for where, text in (("after", f"{FILLER} {n}"), ("before", f"{n} {FILLER}")):
        long = say(text, reader)
        if len(long) != len(alone) or not all(same(x[1], y[1]) for x, y in zip(alone, long)):
            wrong.append(f"{where} the filler: {n[:60]!r}")
print(f"filler of {len(reader.tok(FILLER)['input_ids'])} tokens; {len(notings)} notings, each after it and before it; {len(wrong)} read differently")
print("\n".join("   " + w for w in wrong[:10]))
sys.exit(1 if wrong else 0)
