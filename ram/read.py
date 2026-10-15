"""The reader only points: given the question about one act, the span in the noting that does it, or nothing.
Extractive (deepset/minilm-uncased-squad2 by default, the base rai was trained from); it has no vocabulary to write with.
The span is cut from the noting by character offsets, so it is always the writer's own words, in the writer's own case."""
import re
import torch
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
from transformers.utils import logging

logging.set_verbosity_error()
logging.disable_progress_bar()
BASE = "deepset/minilm-uncased-squad2"
MAX_SPAN = 12
MAX_LENGTH = 384


class Reader:
    def __init__(self, model=BASE):
        self.tok = AutoTokenizer.from_pretrained(model)
        self.tok.truncation_side = "left"  # a noting too long is cut from its start, never at the act
        self.model = AutoModelForQuestionAnswering.from_pretrained(model).eval()

    def read(self, question, noting, end=None):
        """Returns (span, margin). span is None when the reader points at nothing.
        A noting longer than the reader takes is read up to `end` (the close of the act's sentence, from ram.acts), from the
        earliest sentence start that still fits, so the act is never cut off and no sentence is read in part."""
        fits = lambda text: len(self.tok(question, text)["input_ids"]) <= MAX_LENGTH
        if end is not None and not fits(noting):
            noting = noting[:end]
            starts = [0] + [m.end() for m in re.finditer(r"[.;:]\s+", noting)]
            noting = noting[next((s for s in starts if fits(noting[s:])), starts[-1]):]
        enc = self.tok(question, noting, return_tensors="pt", truncation="only_second", max_length=MAX_LENGTH, return_offsets_mapping=True)
        offsets = enc.pop("offset_mapping")[0].tolist()
        with torch.no_grad():
            out = self.model(**enc)
        s, e = out.start_logits[0], out.end_logits[0]
        ctx = [i for i, sid in enumerate(enc.sequence_ids(0)) if sid == 1]
        score, i, j = max(((s[i] + e[j]).item(), i, j) for i in ctx for j in ctx if i <= j < i + MAX_SPAN)
        margin = score - (s[0] + e[0]).item()
        if margin <= 0:
            return None, margin
        return noting[offsets[i][0]:offsets[j][1]], margin
