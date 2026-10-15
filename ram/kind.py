"""Code decides whether a doer counts. A doer counts only when it is particular: a person, a named post, a named section.
A doer in name only does not: the competent authority, the concerned department, the management, it, they.
That is how an office leaves an act to RAM while appearing to name somebody, so the list is here, in plain sight."""
import re

EMPTY = {"by", "the", "a", "an", "all", "this", "that", "these", "higher", "appropriate", "relevant", "necessary"}
NOBODY = {"authority", "authorities", "department", "office", "management", "administration", "system",
          "section", "staff", "team", "it", "one", "they", "we", "someone", "somebody", "concerned", "competent"}


# "by speed post", "by Friday", "by the end of the month": a way of sending or a time, never somebody (rai's grapevine, 13z13)
MEANS = re.compile(r"^(speed |registered )?post$|^courier$|^e-?mail$|^hand$|^fax$|^phone$|^whatsapp$|^mistake$|"
                   r"^(monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow|today)$|^(the )?end of |"
                   r"^(january|february|march|april|may|june|july|august|september|october|november|december)$|"
                   r"^w e f$|^vide$|^puc$")  # office abbreviations are never somebody


# where a number stands decides what it is: after a reference or a body it points at a paper or a place ("Room 12", "Rule 9",
# "Section 12 of the Act"), before a unit of time it is a time ("14 October", "12 noon", "7 days"), with four digits it is a year
# ("GFR-2017"); anywhere else it belongs to a post ("Lab Assistant 3", "UDC-2", "Ward 4 Inspector", "7th CPC")
REFERENCE = {"room", "rule", "rules", "para", "paragraph", "clause", "item", "annexure", "form", "page", "no", "order", "letter",
             "serial", "floor", "block", "wing", "gate", "act"}
TIME = {"noon", "am", "pm", "hrs", "hours", "minutes", "days", "weeks", "months", "years", "january", "february", "march", "april",
        "may", "june", "july", "august", "september", "october", "november", "december"}
ORDINAL = {"st", "nd", "rd", "th"}
# a whole body with a word in front of it is still nobody in particular ("the Executive Management", "the University Administration")
BODY = {"management", "administration"}


def counts(doer):
    doer = re.sub(r"(^|\s+)(w\.?\s?e\.?\s?f\b|vide\b).*$", "", doer, flags=re.I)  # "the Registrar w.e.f. 1 May" is the Registrar
    tokens = re.findall(r"\d+|[a-z]+", doer.lower())
    for n, t in enumerate(tokens):
        if not t.isdigit():
            continue
        before = tokens[n - 1] if n else ""
        after = next((w for w in tokens[n + 1:] if w not in ORDINAL), "")
        if before in NOBODY | REFERENCE or after in TIME or len(t) == 4:
            return False
    words = [w for n, w in enumerate(tokens) if not w.isdigit() and not (w in ORDINAL and n and tokens[n - 1].isdigit())
             and w not in EMPTY]
    if not words or {"concerned", "competent"} & set(words) or MEANS.search(" ".join(words)):
        return False
    return words[-1] not in BODY and not all(w in NOBODY | REFERENCE for w in words)


def short(doer):
    """The doer as said aloud: no leading "by", no leading article, since Hindi has none, and nothing from a "w.e.f." or "vide"
    the reader's span ran on into ("the Registrar w.e.f. 1 May")."""
    doer = re.sub(r"(^|\s+)(w\.?\s?e\.?\s?f\b|vide\b).*$", "", doer, flags=re.I)
    doer = re.sub(r"\s+([,.;:])", r"\1", doer)  # the tokeniser decodes "Officer, Accounts" as "Officer , Accounts"
    return re.sub(r"^(by\s+)?((the|a|an)\s+)?", "", doer.strip(" .,;:"), flags=re.I)
