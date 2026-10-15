#!/usr/bin/env bash
# Every check RAM must pass before a change lands. Run from the repository root, with the trained reader in runs/ram-0.5:
#   bash scripts/check.sh            # uses .venv/bin/python if present, else PYTHON, else python3
set -u
cd "$(dirname "$0")/.."
P="${PYTHON:-}"; [ -n "$P" ] || { [ -x .venv/bin/python ] && P=.venv/bin/python || P=python3; }
"$P" -c 'import torch, transformers, spacy, en_core_web_sm' 2>/dev/null || { echo "$P cannot import torch, transformers, spacy and en_core_web_sm: make the virtual environment first (see the README), or set PYTHON"; exit 1; }
[ -f runs/ram-0.5/model.safetensors ] || { echo "runs/ram-0.5 is missing: download the reader first (see the README)"; exit 1; }
fail=0

printf '\n— no animal product in any script, training row or test noting\n'
"$P" tests/test_vegan.py || fail=1

printf '\n— who counts, called directly\n'
"$P" tests/test_kind.py || fail=1

printf '\n— no training row repeats a sentence of a test noting\n'
"$P" - <<'PY' || fail=1
import json, glob, re
split = lambda t: {s.strip() for s in re.split(r"(?<=\.)\s", t) if s.strip()}
held = set().union(*(split(json.loads(l)["noting"]) for f in glob.glob("tests/notings*.jsonl") for l in open(f)))
contexts = {json.loads(l)["context"] for l in open("data/train-0.5.jsonl")}
leaks = [s for c in contexts for s in split(c) if s in held]
print(f"  {len(contexts)} training notings, {len(held)} held-out sentences, {len(leaks)} repeats")
assert not leaks, f"{len(leaks)} training sentences repeat a test noting, e.g. {leaks[0]!r}"
PY

# the trained reader at threshold 0 must get every act of every test set right, as it did when released
for set in tests/notings*.jsonl; do
  printf '\n— the trained reader on %s\n' "$set"
  line=$("$P" tests/measure.py runs/ram-0.5 "$set" 2>&1 | grep '^reader, threshold 0 ')
  echo "  ${line:-no result}"
  [[ "$line" =~ ([0-9]+)/([0-9]+) ]] && [ "${BASH_REMATCH[1]}" = "${BASH_REMATCH[2]}" ] || { fail=1; echo "  FAILED"; }
done

printf '\n— a noting longer than the reader takes, read act by act\n'
"$P" tests/test_long.py runs/ram-0.5 || fail=1

printf '\n'; [ "$fail" -eq 0 ] && echo "all checks passed" || { echo "SOMETHING FAILED: the change does not land"; exit 1; }
