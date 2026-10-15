"""Measure RAM against the hand-labelled notings, beside a baseline that uses the parser alone.
An answer is right when it says RAM bharose where the gold doer is missing or marked "~" (a title that names nobody, so
ram/kind.py is checked against a fixed answer, never against itself), and names the gold doer (either contains the other)
where it does. Acts the parser finds without a label, and labels it never finds, are listed.
usage: python tests/measure.py [reader] [set]   (default: the untrained base, tests/notings.jsonl)"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ram.acts import NLP, acts
from ram.kind import counts, short
from ram.read import Reader

HERE = os.path.dirname(os.path.abspath(__file__))
rows = [json.loads(l) for l in open(sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "notings.jsonl"))]
norm = lambda t: " ".join(re.sub(r"[^a-z ]", " ", t.lower()).split())


def expected(gold):
    return "RAM bharose" if gold is None or gold.startswith("~") else short(gold)


def right(answer, want):
    if want == "RAM bharose" or answer == "RAM bharose":
        return answer == want
    a, w = norm(answer), norm(want)
    return a in w or w in a


def parser_doer(noting, verb_text):
    """Baseline: the grammatical subject of an active verb, or the 'by' phrase of a passive one."""
    for v in NLP(noting):
        if v.text != verb_text:
            continue
        for c in v.children:
            if c.dep_ == "nsubj":
                return " ".join(t.text for t in c.subtree)
            if c.dep_ == "agent":
                return " ".join(t.text for t in c.subtree)[3:]
    return None


reader = Reader(*sys.argv[1:2])
cases, unlabelled, missed = [], [], []
for row in rows:
    found = {}
    for word, act, question, end in acts(row["noting"]):
        verb = next((w for w in row["doers"] if w.lower() == word.lower() and w not in found), None)
        if verb is None:
            unlabelled.append(f"{act!r} in {row['noting'][:50]}")
            continue
        span, margin = reader.read(question, row["noting"], end)
        found[verb] = True
        cases.append(dict(verb=verb, question=question, gold=row["doers"][verb], want=expected(row["doers"][verb]), span=span, margin=margin,
                          parser=parser_doer(row["noting"], verb), noting=row["noting"]))
    missed += [f"{w!r} in {row['noting'][:50]}" for w in row["doers"] if w not in found]


def answer(span, ok):
    return short(span) if span and ok and counts(span) else "RAM bharose"


# the threshold: the lowest margin at which the reader points at nothing for any act whose noting names no doer at all.
# Acts whose doer is a title naming nobody ("~") are left out: pointing there is right, and refusing it is kind.py's job.
leaks = [c["margin"] for c in cases if c["gold"] is None and c["span"]]
threshold = max(leaks + [0.0])

for name, pick in [("reader, threshold 0", lambda c: answer(c["span"], c["margin"] > 0)),
                   (f"reader, threshold {threshold:.2f}", lambda c: answer(c["span"], c["margin"] > threshold)),
                   ("parser alone", lambda c: answer(c["parser"], True))]:
    n = sum(right(pick(c), c["want"]) for c in cases)
    print(f"{name:<26} {n}/{len(cases)} right")
    for c in cases:
        got = pick(c)
        if not right(got, c["want"]):
            print(f"   {c['verb']:<11} want {c['want']!r:<34} got {got!r}  ({c['question']}; margin {c['margin']:.2f})")
print(f"\nacts found but not labelled: {len(unlabelled)}")
for u in unlabelled:
    print("  ", u)
print(f"labels never found as acts: {len(missed)}")
for m in missed:
    print("  ", m)
