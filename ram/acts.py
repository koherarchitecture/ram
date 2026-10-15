"""Code finds the acts: every verb in the noting that somebody has to do. No model decides which acts there are.
Each act comes with the one question the reader is asked about it, built from the writer's own words."""
import re
import spacy

NLP = spacy.load("en_core_web_sm")
# office abbreviations the parser does not know, read as plain words before parsing ("has been prepared w.e.f. 1 May" otherwise
# parses "prepared" as an adjective of "w.e.f."). The parse, the act as shown and the question use this copy; the reader reads the writer's own text.
PLAIN = re.compile(r"\bw\.?\s?e\.?\s?f\.?(?=\s)|\bvide\b", re.I)
# not acts: "all concerned" names people; noting prose uses "dated", "amounting to", "regarding", "Earned Leave", "Leave applications"
# as prepositions and names
NOT_ACTS = {"be", "have", "seem", "appear", "need", "wish", "concern", "show", "date", "amount", "regard", "earn", "leave"}
# papers an office moves: at the head of a fragment they are what was acted on, even when the parser takes them for a name ("Bill received")
PAPERS = {"bill", "bills", "file", "files", "letter", "letters", "application", "applications", "proposal", "invoice", "quotation",
          "quotations", "tender", "tenders", "cheque", "report", "note", "draft", "memo", "circular", "representation", "complaint",
          "request", "claim", "voucher", "notice", "reply"}


def fragment(verb):
    """The thing a noting fragment acts on, when the fragment drops its "was": "File received", "Bills received from the supplier".
    A past verb with no auxiliary and no object whose subject is a bare common noun, with no "the", reads as a passive."""
    if verb.tag_ not in ("VBD", "VBN") or any(c.dep_ in ("aux", "auxpass", "dobj") for c in verb.children):
        return None
    return next((c for c in verb.children if c.dep_ == "nsubj" and (c.tag_ in ("NN", "NNS") or c.lower_ in PAPERS)
                 and not any(g.dep_ in ("det", "poss") for g in c.children)), None)


def plain(noting):
    """The copy the parser reads, and for each place in it (and its end), the same place in the writer's own text."""
    copy, where, last = "", [], 0
    for m in PLAIN.finditer(noting):
        word = "under" if m.group(0).lower() == "vide" else "from"
        copy += noting[last:m.start()] + word
        where += list(range(last, m.start())) + [m.start()] * len(word)
        last = m.end()
    return copy + noting[last:], where + list(range(last, len(noting) + 1))


def acts(noting):
    """Returns a list of (verb, act, question, end): the verb as written, the act as shown (verb and object, the object cut to
    six words), the one question the reader is asked about it, and where in the writer's text the act's sentence ends,
    so a noting too long for the reader is read up to there."""
    found = []
    copy, where = plain(noting)
    doc = NLP(copy)
    for verb in doc:
        if verb.pos_ != "VERB" or verb.lemma_ in NOT_ACTS or verb.dep_ in ("amod", "compound") or not verb.is_alpha:
            continue  # "the broken tiles", "the cleaning contractor", "w.e.f."
        # a present verb with no subject of its own is a noun misread ("the patient admission register daily")
        if verb.tag_ in ("VBP", "VBZ") and not any(c.dep_ in ("nsubj", "nsubjpass", "expl") for c in verb.children):
            continue
        # a participle hanging off a noun is a description ("an application dated 12/10", "quotation amounting to"),
        # unless it names who did it ("the report prepared by DR (Accounts)"), or the noun is the whole fragment ("Draft reply placed below")
        headed = verb.dep_ == "acl" and verb.head.dep_ == "ROOT" and verb.head.pos_ in ("NOUN", "PROPN")
        if verb.dep_ == "acl" and not headed and not any(c.dep_ == "agent" for c in verb.children):
            continue
        bare = fragment(verb)
        obj = verb.head if headed else bare or next((c for c in verb.children if c.dep_ in ("dobj", "nsubjpass")), None)
        # "checked by me and found in order": the second verb shares the first one's passive and its object
        shared = verb.dep_ == "conj" and not obj and not any(c.dep_ == "nsubj" for c in verb.children)
        if shared:
            obj = next((c for c in verb.head.children if c.dep_ == "nsubjpass"), None) or fragment(verb.head)
        # "Draft reply placed below.": the noun without its own participle or the full stop
        inside = {t.i for t in verb.subtree} | {c.i for c in obj.children if c.dep_ == "punct"} if headed else set()
        what = " ".join(t.text for t in obj.subtree if t.i not in inside) if obj else ""
        if obj is not None and obj.tag_ in ("WDT", "WP") and verb.dep_ == "relcl":  # "the medical bills, which may be approved by"
            what = " ".join(t.text for t in verb.head.subtree if t.i < verb.head.i or t.i == verb.head.i)
        if obj and obj.left_edge.is_sent_start and obj.left_edge.pos_ != "PROPN":
            what = what[0].lower() + what[1:]  # "The file was received" asks "By whom was the file received?"
        passive = any(c.dep_ == "auxpass" for c in verb.children) or ((shared or bare or headed) and obj is not None)
        modal = " ".join(c.text for c in verb.children if c.tag_ == "MD")
        if passive:
            question = f"By whom was {what} {verb.text}?" if what else f"Who {verb.text} it?"
        elif modal:
            question = f"Who {modal} {verb.lemma_} {what}?"
        elif verb.tag_ == "VB":
            question = f"Who is to {verb.lemma_} {what}?"
        else:
            question = f"Who {verb.text} {what}?"
        shown = " ".join(what.split()[:6]) + (" …" if len(what.split()) > 6 else "")
        act = f"{shown} {verb.text}" if passive and what and what.lower() != "it" else f"{verb.text} {shown}"
        found.append((verb.text, act.strip(), " ".join(question.split()), where[verb.sent.end_char]))
    return found
