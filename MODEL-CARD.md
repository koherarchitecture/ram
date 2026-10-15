---
license: cc-by-4.0
language:
- en
library_name: transformers
pipeline_tag: question-answering
base_model: deepset/minilm-uncased-squad2
tags:
- extractive-question-answering
- agency
- office-writing
- split-domain-cognition
- synthetic-data
- cpu
---

# RAM reader 0.5 — model card

**What it is.** An extractive question-answering model. Given a question about one act in a piece of office writing (*Who approved the proposal?*, *By whom was the file received?*) and the writing itself, it returns the span that does the act, or nothing. It cannot generate text. It is the reading part of [RAM](https://github.com/koherarchitecture/ram), in which code finds the acts, builds the questions and decides whether a span names somebody who counts.

**Trained from.** [deepset/minilm-uncased-squad2](https://huggingface.co/deepset/minilm-uncased-squad2) (CC-BY-4.0), deepset's fine-tune of Microsoft's [MiniLM-L12-H384-uncased](https://huggingface.co/microsoft/MiniLM-L12-H384-uncased) (MIT) on SQuAD 2.0. Same architecture, 33M parameters, nothing added.

**Trained on.** 14,000 synthetic rows from `scripts/synth.py` (seed 7), labels known by construction: office notings built from word lists, each act asked the question RAM's act finder asks, with the doer the generator placed or none. The rows cover named people, posts, roles and sections; titles that name nobody; *by* phrases that are a means or a time; negated passives, joined verbs, relative clauses, recipients and deciders, noting fragments, lowercase typing, and two clauses with their own subjects where only the first names a doer. About two notings in five are placed among other notings, and only their own acts are labelled (details in the README). No training sentence repeats a test sentence; four test names are training names. No row names an animal product (`tests/test_vegan.py`).

**Training.** 2 passes at learning rate 2e-5, batch 16, AdamW, with seeds 7, 1 and 2, whose weights are averaged into one reader. About 155 seconds a seed on an NVIDIA GB10.

**Measured** at a no-answer margin of 0 (the reader returns its best span whenever it scores above the no-answer score), with RAM's rule for who counts applied (`ram/kind.py`), RAM gets every act right in the five test sets of the README's table: 39, 35, 24, 43 and 37 acts. The parser alone, through the same rule, gets 38, 32, 20, 36 and 36. Placed after or before about 530 tokens of unrelated references, every one of the 99 test notings gets the same answers as alone (`tests/test_long.py`).

**Limits.**
- Every test set has been seen, and each led to a fix; one, `notings-forms.jsonl`, was written from failures and was never blind.
- All five test sets were written by models (three in Claude Code, two by Gemini 3, keyed by hand). Performance on office writing by people is not measured.
- On plain writing, a parser's subject or *by* phrase does nearly as well (README, *What these numbers do not show*).
- English in Roman letters only.
- The reader takes 384 tokens of question and writing. RAM reads longer writing act by act, up to the end of the act's sentence; a doer after that sentence, or too far before it to fit, is not read.
- The reader alone is not RAM. It is trained to point at a title that names nobody (*the competent authority*) as it points at a person, and refusing the title is left to `ram/kind.py`; without that rule and the act finder, its span alone does not show whether a doer who counts is named.

**Intended use.** Inside RAM, for the person who wrote the sentence, on their own draft. **Not for** judging somebody else's writing, or as a step in any decision about anybody.

**Credit.** RAM reader by Koher, trained from deepset/minilm-uncased-squad2 by deepset (CC-BY-4.0), itself trained from Microsoft's MiniLM-L12-H384-uncased (MIT).
