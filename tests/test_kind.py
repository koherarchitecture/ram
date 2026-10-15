"""ram/kind.py on inputs written for it, not only on what the reader happens to point at (rai's grapevine, 13z36).
usage: python tests/test_kind.py"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ram.kind import counts, short

SOMEBODY = ["Ms Rao", "by Ms Rao", "the Registrar", "by the Registrar", "I", "the Section Officer, Accounts", "Shri Negi",
            "Lab Assistant 3", "UDC-2", "the Legal Department", "the Library staff",
            "Ward 4 Inspector", "the 7th CPC cell", "Room Attendant", "Floor Manager", "the Registrar w.e.f. 1 May"]
NOBODY = ["the competent authority", "the concerned department", "this office", "the management", "it", "they", "we",
          "by speed post", "by email", "by Friday", "by the end of the month", "14 October", "w.e.f.", "", "the",
          "Room 12", "Rule 9", "Section 12", "the Executive Management", "the University Administration",
          "Section 12 of the Act", "vide letter dated 3 May", "w.e.f. 1 May", "12 noon", "7 days", "14th October", "20 November 2026", "12/10/2026", "GFR-2017", "Room 12, Block B",
          "the 3rd floor"]
SAID = {"by the Registrar": "Registrar", "the Registrar w.e.f. 1 May": "Registrar", "Ms Rao vide letter 12": "Ms Rao", "The Section Officer , Accounts": "Section Officer, Accounts", "by Ms Rao": "Ms Rao"}

wrong = [f"counts({d!r}) should be True" for d in SOMEBODY if not counts(d)]
wrong += [f"counts({d!r}) should be False" for d in NOBODY if counts(d)]
wrong += [f"short({d!r}) is {short(d)!r}, should be {w!r}" for d, w in SAID.items() if short(d) != w]
print("\n".join(wrong) or f"kind: {len(SOMEBODY) + len(NOBODY) + len(SAID)} cases right")
sys.exit(1 if wrong else 0)
