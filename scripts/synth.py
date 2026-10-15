"""Write RAM's training rows: office notings built from word lists, each act asked the question RAM will be asked, labelled with
the doer the generator put there, or none. The questions come from ram.acts itself, so training asks exactly what reading asks.
usage: python scripts/synth.py [--rows 9000] [--seed 7] > data/train.jsonl
Held out by text: no sentence of any tests/notings*.jsonl appears here. Names are not held out: four test names (Suresh, Sunita, Nair, Rao)
are also in the lists below."""
import argparse, json, os, random, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from ram.acts import acts

FIRST = ["Rekha", "Suresh", "Farida", "Joseph", "Lakshmi", "Harpreet", "Imran", "Kavita", "Venkat", "Anjali", "Tenzin", "Bhavesh",
         "Nandini", "Arjun", "Sunita", "Mohan", "Zoya", "Gopal", "Meena", "Rafiq", "Deepa", "Sanjay", "Ritu", "Thomas", "Pooja"]
FAMILY = ["Iyer", "Shah", "Sheikh", "D'Souza", "Reddy", "Gill", "Qureshi", "Nair", "Rao", "Bhatt", "Lepcha", "Chauhan", "Menon",
          "Desai", "Kulkarni", "Ansari", "Pillai", "Trivedi", "Banerjee", "Fernandes", "Solanki", "Parmar", "Ghosh", "Bose"]
HONOUR = ["Mr", "Ms", "Mrs", "Dr", "Shri", "Smt"]
POSTS = ["the Registrar", "the Dean", "the Head of Department", "the Controller of Examinations", "the cashier", "the hostel warden",
         "the lab assistant", "the librarian", "the purchase officer", "the estate manager", "the security supervisor", "the electrician",
         "the driver", "the store keeper", "the IT coordinator", "the Vice-Chancellor", "the Section Officer, Establishment",
         "the Assistant Registrar, Academics", "the office assistant", "the accountant", "the plumber", "the course coordinator"]
ROLES = ["the applicant", "the beneficiary", "the auditor", "the supplier", "the tenant", "the candidate", "the undersigned",
         "the bidder", "the transporter", "the caretaker", "the HoD", "the AO", "the DR (Academics)", "the bank", "the visiting team"]
BARE = ["Admissions", "Establishment", "Examinations", "Stores", "Purchase", "Legal", "Security", "Housekeeping"]  # sections named bare
SECTIONS = ["the Accounts section", "the Purchase cell", "the Examination cell", "the Admissions office", "the Estate Office",
            "the Placement cell", "the Library staff", "the Stores section"]
NOBODY = ["the competent authority", "the concerned department", "higher authorities", "the management", "the administration",
          "the concerned section", "the department", "this office", "all concerned", "this section"]
AWAY = ["by email", "by post", "by courier", "by hand", "by Friday", "by Monday", "by 20 November", "by the end of the week",
        "by the end of the month", "by mistake", "from the vendor", "from the bank", "from the head office", "on Tuesday",
        "through proper channel", "with immediate effect", "before the inspection", "after the meeting", "in triplicate"]
# base, past, participle, objects: plain office acts, none naming an animal product (Koher policy, 23 September 2026)
ACTS = [("approve", "approved", "approved", ["the proposal", "the budget", "the request for two laptops"]),
        ("verify", "verified", "verified", ["the bills", "the attendance register", "the hall tickets"]),
        ("forward", "forwarded", "forwarded", ["the file", "the complaint", "the application"]),
        ("sanction", "sanctioned", "sanctioned", ["the advance", "the leave", "the travel grant"]),
        ("release", "released", "released", ["the payment", "the salary arrears", "the deposit"]),
        ("sign", "signed", "signed", ["the invoice", "the certificates", "the agreement"]),
        ("repair", "repaired", "repaired", ["the water cooler", "the projector in Room 12", "the lift"]),
        ("book", "booked", "booked", ["the seminar hall", "the bus for the visit", "the guest house"]),
        ("circulate", "circulated", "circulated", ["the minutes", "the notice", "the revised schedule"]),
        ("install", "installed", "installed", ["the printer", "the new antivirus", "the CCTV cameras"]),
        ("inspect", "inspected", "inspected", ["the hostel rooms", "the fire extinguishers", "the construction site"]),
        ("issue", "issued", "issued", ["the circular", "the identity cards", "the purchase order"]),
        ("prepare", "prepared", "prepared", ["the duty roster", "the annual report", "the seating plan"]),
        ("send", "sent", "sent", ["the reminder", "the quotation", "the marks list"]),
        ("update", "updated", "updated", ["the stock register", "the website", "the fee records"]),
        ("cancel", "cancelled", "cancelled", ["the order", "the tender", "the booking"]),
        ("collect", "collected", "collected", ["the answer sheets", "the keys", "the cheques"]),
        ("review", "reviewed", "reviewed", ["the draft rules", "the shortlist", "the audit remarks"]),
        ("arrange", "arranged", "arranged", ["the chairs", "the transport", "the refreshments"]),
        ("replace", "replaced", "replaced", ["the broken window", "the fused tube lights", "the old furniture"]),
        ("assign", "assigned", "assigned", ["additional charge of the Stores", "the invigilation duty", "the inquiry"]),
        ("submit", "submitted", "submitted", ["the file", "the estimate", "the compliance report"]),
        ("place", "placed", "placed", ["the file", "the draft reply", "the tender papers"])]
DECIDE = ["orders", "approval", "signature", "perusal", "sanction", "kind consideration"]


def person():
    r = random.random()
    if r < 0.35:
        return f"{random.choice(HONOUR)} {random.choice(FAMILY)}"
    if r < 0.5:
        return f"{random.choice(FIRST)} {random.choice(FAMILY)}"
    if r < 0.6:
        return random.choice(FIRST) + random.choice(["", f" from {random.choice(SECTIONS)[4:]}"])
    if r < 0.75:
        return random.choice(POSTS)
    if r < 0.87:
        return random.choice(ROLES)
    if r < 0.94:
        return random.choice(BARE)
    return random.choice(SECTIONS)


def cap(s):
    return s[0].upper() + s[1:]


def tail():
    return " " + random.choice(AWAY) if random.random() < 0.5 else ""


def sentence(used):
    """One sentence and its labels: {verb as written: doer or None}. Never repeats a verb already in the noting."""
    pick = [a for a in ACTS if a[1] not in used and a[2] not in used and a[0] not in used]
    base, past, pp, objs = random.choice(pick)
    o = random.choice(objs)
    d = person() if random.random() < 0.85 else random.choice(NOBODY)
    shape = random.randrange(20)
    if shape == 0:
        return f"{cap(d)} {past} {o}{tail()}.", {past: d}
    if shape == 1:
        m = random.choice(["will", "may", "should", "shall"])
        return f"{cap(d)} {m} {base} {o}{tail()}.", {base: d}
    if shape == 2:
        aux = random.choice(["was", "has been", "had been"])
        return f"{cap(o)} {aux} {pp} by {d}{tail()}.", {pp: d}
    if shape in (3, 4):  # the doerless act, often beside a "by" or "from" that is not a doer
        aux = random.choice(["was", "has been", "will be", "may be", "is to be", "could not be", "should be"])
        return f"{cap(o)} {aux} {pp} {random.choice(AWAY)}.", {pp: None}
    if shape == 5:
        return f"{random.choice(['Kindly', 'May kindly', 'Please'])} {base} {o}{tail()}.", {base: None}
    if shape == 6:
        return f"It was decided to {base} {o}{tail()}.", {"decided": None, base: None}
    if shape == 7:
        rest = [a for a in pick if a[0] != base]
        b2, past2, pp2, objs2 = random.choice(rest)
        return f"{cap(d)} {past} {o} and {past2} {random.choice(objs2)}.", {past: d, past2: d}
    if shape == 8:
        return f"{cap(d)} is requested to {base} {o}{tail()}.", {"requested": None, base: d}
    if shape == 9:
        pro = random.choice(["I", "We"])
        return f"{pro} {past} {o}{tail()}.", {past: pro}
    rest = [a for a in pick if a[0] != base]
    b2, past2, pp2, objs2 = random.choice(rest)
    if shape == 19:  # 0.5: two clauses, each with its own subject; the doer of the first is not the doer of the second
        aux2 = random.choice(["was", "were", "has been", "have been"])
        return f"{cap(o)} {random.choice(['was', 'were', 'has been'])} {pp} by {d} and {random.choice(objs2)} {aux2} {pp2}{tail()}.", {pp: d, pp2: None}
    if shape == 10:  # a negated passive keeps its doer
        return f"{cap(o)} {random.choice(['was not', 'has not been', 'could not be'])} {pp} by {d}{tail()}.", {pp: d}
    if shape == 11:  # a second passive verb shares the first one's doer
        return f"{cap(o)} {random.choice(['was', 'were'])} {pp} by {d} and {pp2} in order.", {pp: d, pp2: d}
    if shape == 12:  # a relative clause names the same doer for both acts
        return f"{cap(d)}, who had {pp} {o}, has now {pp2} {random.choice(objs2)}.", {pp: d, pp2: d}
    if shape == 13:
        return f"{cap(o)} was {pp} {random.choice(AWAY)}, as {random.choice(['confirmed', 'reported', 'certified'])} by {d}.", \
            {pp: None, **{w: d for w in ["confirmed", "reported", "certified"]}}
    d2 = person()
    while d2 == d:
        d2 = person()
    if shape == 15:  # the one it goes TO is a recipient, not the doer
        if random.random() < 0.5:
            return f"{cap(o)} {random.choice(['may be', 'has been', 'is'])} {pp} to {d2}{tail()}.", {pp: None}
        return f"{cap(d)} {past} {o} to {d2}{tail()}.", {past: d}
    if shape == 16:  # "for orders of" and "for sanction by" name who will decide, not who submits
        return f"{cap(o)} is {pp} for {random.choice(DECIDE)} {random.choice(['of', 'by'])} {d2}.", {pp: None}
    if shape == 17:  # the doer named once, on the second of two joined verbs, belongs to both
        return f"{cap(o)} {random.choice(['have been', 'were', 'has been'])} {pp} and {pp2} by {d}{tail()}.", {pp: d, pp2: d}
    frag = random.choice([("Submitted for approval please.", {"Submitted": None}), ("Approved as proposed.", {"Approved": None, "proposed": None}),
                          (f"Orders may be issued {random.choice(AWAY)}.", {"issued": None}), (f"Put up for {random.choice(['orders', 'perusal', 'signature'])}.", {"Put": None}),
                          ("Seen, thanks.", {"Seen": None}), (f"Necessary instructions have been given to {random.choice(NOBODY)}.", {"given": None})])
    return frag


def noting():
    text, labels = [], {}
    for _ in range(random.choice([1, 2, 2, 3])):
        s, lab = sentence(labels)
        text.append(s); labels.update(lab)
    text = " ".join(text)
    if random.random() < 0.15:  # typed as people type: lower case, no closing full stop (rai's grapevine, 13z9)
        text, labels = text.lower().rstrip("."), {k.lower(): (v.lower() if v else v) for k, v in labels.items()}
    return text, labels


def rows_for(text, labels, first=0, last=None):
    """Rows for the acts of the noting that runs from `first` to `last` in `text`; anything around it is other notings."""
    last = len(text) if last is None else last
    out = []
    for verb, act, question, end in acts(text):
        if verb not in labels or not first < end <= last:
            continue
        doer = labels[verb]
        start = text.find(cap(doer), first) if doer and text.find(cap(doer), first) >= 0 else (text.find(doer, first) if doer else -1)
        if doer and start < 0:
            continue
        span = text[start:start + len(doer)] if doer else None
        out.append({"question": question, "context": text, "span": span, "start": start})
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=9000); ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    random.seed(a.seed)
    tests = os.path.join(ROOT, "tests")
    held = [json.loads(l)["noting"] for f in sorted(os.listdir(tests)) if f.startswith("notings") and f.endswith(".jsonl") for l in open(os.path.join(tests, f))]
    held_sentences = {s.strip() for n in held for s in re.split(r"(?<=\.)\s", n)}
    n = 0
    while n < a.rows:
        text, labels = noting()
        # 0.4: in two rows of five the noting sits among other notings, whose doers are not its doers (rai's grapevine, 13z38)
        before = [noting()[0] for _ in range(random.randint(1, 3))] if random.random() < 0.4 else []
        after = [noting()[0] for _ in range(random.randint(0, 2))] if before and text.endswith(".") else []
        first = len(" ".join(before)) + (1 if before else 0)
        whole = " ".join(before + [text] + after)
        if any(s.strip() in held_sentences for s in re.split(r"(?<=\.)\s", whole)):
            continue
        for r in rows_for(whole, labels, first, first + len(text)):
            print(json.dumps(r)); n += 1
