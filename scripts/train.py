"""Continue the reader from deepset's weights on RAM's rows: rai's recipe (2 passes at 2e-5, batch 16), nothing added.
usage: python scripts/train.py --data data/train-0.5.jsonl --out runs/ram-0.5-s7 --seed 7
       python scripts/train.py --soup runs/ram-0.5 runs/ram-0.5-s7 runs/ram-0.5-s1 runs/ram-0.5-s2
The soup averages the weights of readers trained from the same start (rai's grapevine, 13o)."""
import argparse, json, os, random, sys, time
import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ram.read import BASE

ap = argparse.ArgumentParser()
ap.add_argument("--data"); ap.add_argument("--out"); ap.add_argument("--seed", type=int, default=7)
ap.add_argument("--soup", nargs="+", help="OUT then the readers to average")
a = ap.parse_args()
dev = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"

if a.soup:
    out, *parts = a.soup
    models = [AutoModelForQuestionAnswering.from_pretrained(p) for p in parts]
    state = {k: sum(m.state_dict()[k] for m in models) / len(models) for k in models[0].state_dict()}
    models[0].load_state_dict(state); models[0].save_pretrained(out)
    AutoTokenizer.from_pretrained(parts[0]).save_pretrained(out)
    print(f"souped {len(parts)} readers into {out}")
    raise SystemExit

torch.manual_seed(a.seed); random.seed(a.seed)
rows = [json.loads(l) for l in open(a.data)]
tok = AutoTokenizer.from_pretrained(BASE)
model = AutoModelForQuestionAnswering.from_pretrained(BASE).to(dev)


def features(batch):
    enc = tok([r["question"] for r in batch], [r["context"] for r in batch], truncation="only_second", max_length=384,
              padding=True, return_offsets_mapping=True, return_tensors="pt")
    starts, ends = [], []
    for i, r in enumerate(batch):
        s = e = 0  # no doer -> [CLS]
        if r["span"]:
            cs, ce = r["start"], r["start"] + len(r["span"])
            ids = enc.sequence_ids(i)
            for t, (o0, o1) in enumerate(enc["offset_mapping"][i].tolist()):
                if ids[t] != 1:
                    continue
                if o0 <= cs < o1 and s == 0: s = t
                if o0 < ce <= o1: e = t
            if e < s: s = e = 0
        starts.append(s); ends.append(e)
    del enc["offset_mapping"]
    enc["start_positions"] = torch.tensor(starts); enc["end_positions"] = torch.tensor(ends)
    return enc


opt = torch.optim.AdamW(model.parameters(), lr=2e-5)
loader = DataLoader(rows, batch_size=16, shuffle=True, collate_fn=features)
model.train(); t0 = time.time(); step = 0
for ep in range(2):
    for batch in loader:
        loss = model(**{k: v.to(dev) for k, v in batch.items()}).loss
        loss.backward(); opt.step(); opt.zero_grad(); step += 1
        if step % 100 == 0:
            print(f"seed {a.seed} epoch {ep + 1} step {step} loss {loss.item():.3f} {time.time() - t0:.0f}s", flush=True)
model.save_pretrained(a.out); tok.save_pretrained(a.out)
json.dump({"device": dev, "base": BASE, "data": a.data, "rows": len(rows), "epochs": 2, "lr": 2e-5, "batch": 16, "seed": a.seed,
           "seconds": round(time.time() - t0)}, open(f"{a.out}/training.json", "w"), indent=1)
print(f"saved {a.out} after {time.time() - t0:.0f}s")
