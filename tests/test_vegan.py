"""No text RAM is trained or tested on names an animal product. Scans the code, the script that writes the training data, the
training data and every test set, and fails on any match. The word list is rai's (github.com/koherarchitecture/rai), so the two
models are held to one list. Plant milks (soy, oat, almond, coconut, rice, plant) and peanut butter are allowed.
usage: python tests/test_vegan.py"""
import glob, os, re, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORDS = r"milk|milky|dairy|curd|dahi|ghee|paneer|butter|buttermilk|chaas|lassi|cream|cheese|yogh?urt|eggs?|omelettes?|meat|chicken|mutton|beef|pork|bacon|ham|fish|prawns?|shrimps?|crabs?|honey|leather|wool|woollen|silk|suede|fur|feathers?|gelatine?|lard|malai|kheer|khoya|mawa|rabdi|pearls?|ivory|beeswax|lanolin|shellac|mayonnaise|mayo|doodh|dudh|makhan|makkhan|anda|ande|andey|machli|machhli|machi|gosht|murga|murgi|keema|kheema|shahad|shehad|chamda|chamde|resham|reshmi|nonveg|non-veg"
ANIMAL = re.compile(rf"\b({WORDS})\b", re.I)
ALLOWED = re.compile(r"\b(soy|oat|almond|coconut|rice|plant) milk\b|\bpeanut butter\b", re.I)

hits = [f"{os.path.relpath(p, HERE)}:{n}: {m.group(0)}"
        for pattern in ["ram/*.py", "scripts/*.py", "data/*.jsonl", "tests/notings*.jsonl"]
        for p in sorted(glob.glob(os.path.join(HERE, pattern)))
        for n, line in enumerate(open(p, encoding="utf-8"), 1) for m in ANIMAL.finditer(ALLOWED.sub("", line))]
print("\n".join(hits) or "vegan scan: 0")
sys.exit(1 if hits else 0)
