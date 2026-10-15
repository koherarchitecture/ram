<h1 align="center">RAM</h1>

<p align="center"><strong>A model that points at who is doing each act in a piece of office writing.</strong></p>

<p align="center">
  <a href="https://github.com/koherarchitecture/ram/releases/tag/v0.5"><img src="https://img.shields.io/badge/release-v0.5-D59A3A" alt="release v0.5"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/code-AGPL--3.0-373E3C" alt="code licence AGPL-3.0"></a>
  <a href="LICENSE-WEIGHTS-AND-DATA.md"><img src="https://img.shields.io/badge/weights_%26_data-CC--BY--4.0-373E3C" alt="weights and data licence CC-BY-4.0"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-3776AB" alt="Python 3.10+">
  <a href="https://github.com/koherarchitecture/ram/releases/download/v0.5/ram-reader-0.5.tar.gz"><img src="https://img.shields.io/badge/reader-122_MB_download-D59A3A" alt="reader, 122 MB download"></a>
</p>
<p align="center">
  <img src="https://img.shields.io/badge/reader-extractive%2C_33M_parameters-E8B86D" alt="extractive reader, 33M parameters">
  <img src="https://img.shields.io/badge/parser-spaCy_en__core__web__sm-E8B86D" alt="parser spaCy en_core_web_sm">
  <img src="https://img.shields.io/badge/runs_on-CPU-E8B86D" alt="runs on CPU">
  <img src="https://img.shields.io/badge/training_data-100%25_synthetic-E8B86D" alt="training data 100% synthetic">
  <img src="https://img.shields.io/badge/output-%3Cdoer%3E_karega_%2F_RAM_bharose-E8B86D" alt="output is <doer> karega or RAM bharose">
  <img src="https://img.shields.io/badge/language-English%2C_Roman_letters-E8B86D" alt="English in Roman letters">
</p>
<p align="center">
  <img src="https://img.shields.io/badge/test_acts-178_of_178-2E7D5B" alt="178 of 178 test acts">
  <img src="https://img.shields.io/badge/parser_alone-162_of_178-6B6B6B" alt="parser alone 162 of 178">
  <img src="https://img.shields.io/badge/long_notings-99_of_99_steady-2E7D5B" alt="99 of 99 notings read the same beside long text">
  <img src="https://img.shields.io/badge/test_sets-written_by_models-B5523B" alt="test sets written by models">
  <img src="https://img.shields.io/badge/people's_notings-not_measured-B5523B" alt="notings written by people not measured">
</p>
<p align="center">
  <img src="https://img.shields.io/badge/vegan_scan-0_hits-2E7D5B" alt="vegan scan 0 hits">
  <img src="https://img.shields.io/badge/logging-none-2E7D5B" alt="no logging">
  <img src="https://img.shields.io/badge/network_after_download-none-2E7D5B" alt="no network after the download">
  <img src="https://img.shields.io/badge/writes-no_word_of_its_own-2E7D5B" alt="writes no word of its own">
  <a href="https://splitdomaincognition.org"><img src="https://img.shields.io/badge/follows-Split--Domain_Cognition-2E7D5B" alt="follows Split-Domain Cognition"></a>
  <a href="https://github.com/koherarchitecture/rai"><img src="https://img.shields.io/badge/sibling-rai-2E7D5B" alt="sibling of rai"></a>
</p>

---

RAM (It's RAM; not Ram.) reads a short piece of office writing, such as a file noting or an email, and finds every act in it: each thing somebody has to do. For each act it says ***<doer> karega*** (Hindi, *"<doer> will do it"*) when the writing names somebody who does it, or ***RAM bharose*** when it leaves the act to nobody.

```
$ echo "The matter has been examined and the competent authority has approved the proposal. Necessary action may be taken." | python -m ram
the matter examined                      RAM bharose
approved the proposal                    RAM bharose
necessary action taken                   RAM bharose

$ echo "I examined the matter. The Registrar approved the proposal on 14 October. The Section Officer, Accounts, will release the payment." | python -m ram
examined the matter                      I karega
approved the proposal                    Registrar karega
release the payment                      Section Officer, Accounts karega
```

The model returns the span of the writing that does the act, or nothing. Code decides everything else, in `acts.py`, `kind.py` and `__main__.py`; the reader is called from `read.py`. The four files are 201 lines together.

**The name.** *राम भरोसे छोड़ना*, *to leave something to Ram*, means to leave something to chance because nobody is in charge. People in India say it of an office where nobody owns the work. Written in capitals, the model's name also reads as computer memory, and an act that names nobody is left to it: *RAM bharose*. The project built on the model is *bharose chhodna*, so bharose chhodna runs on RAM.

## Contents

- [Quick start](#quick-start)
- [Use it from Python](#use-it-from-python)
- [What it is for](#what-it-is-for)
- [How it works](#how-it-works)
- [How well it reads](#how-well-it-reads)
- [What RAM does not do](#what-ram-does-not-do)
- [What RAM is not for](#what-ram-is-not-for)
- [Model, data and training](#model-data-and-training)
- [Repository layout](#repository-layout)
- [Licences and credit](#licences-and-credit)

## Quick start

```bash
git clone https://github.com/koherarchitecture/ram.git
cd ram
python3 -m venv .venv
.venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu   # optional: torch's CPU build, several GB smaller on Linux
.venv/bin/pip install -r requirements.txt     # torch, transformers, spaCy and spaCy's small English model

# the trained reader, 122 MB, from this release
curl -L -o ram-reader-0.5.tar.gz https://github.com/koherarchitecture/ram/releases/download/v0.5/ram-reader-0.5.tar.gz
sha256sum -c ram-reader-0.5.tar.gz.sha256      # the .sha256 file comes with the clone; on macOS use shasum -a 256 -c
mkdir -p runs && tar -xzf ram-reader-0.5.tar.gz -C runs/    # creates runs/ram-0.5/

echo "Necessary action may be taken." | .venv/bin/python -m ram
```

Once the reader is downloaded, everything runs locally on a CPU. Nothing you type is sent anywhere or kept after the command ends.

Tested from a fresh copy with Python 3.12, torch 2.14, transformers 5.19 and spaCy 3.8 on Linux (x86-64). The reader was trained and first measured on macOS (Apple silicon).

## Use it from Python

```python
from ram.__main__ import say, READER
from ram.read import Reader

reader = Reader(READER)          # load once
for act, answer in say("The bill was checked by Ms Rao. Necessary action may be taken.", reader):
    print(act, "→", answer)
```

`say` and `READER` live in `ram/__main__.py`, the module `python -m ram` runs; `READER` is an absolute path to `runs/ram-0.5` inside the repository. `say` returns a list of `(act, answer)` pairs, one per act, in the order the acts appear: here `("the bill checked", "Ms Rao karega")` and `("necessary action taken", "RAM bharose")`.

## What it is for

An office often writes the doer out of the sentence: *action will be taken*, *your application could not be processed*. The act still has to be done, and the file moves between desks until somebody notices that nobody was given it. RAM marks each such act in a draft before the writer sends it.

## How it works

1. **Code finds the acts** ([`ram/acts.py`](ram/acts.py)). spaCy's small English parser marks every verb somebody has to do, and code builds one fixed question for each: *Who approved the proposal?*, *By whom was the file received?*, *Who will release the payment?* Office abbreviations the parser does not know are read as plain words first (*w.e.f.* as "from", *vide* as "under"), and a noting fragment that drops its *was* is read as a passive: a past verb with no auxiliary and no object, whose subject is a bare common noun or a paper an office moves (*File received.*, *Application received and examined.*, *Bill received from the supplier.*). A relative *which* is asked about the noun it stands for (*By whom was the medical bills approved?*, the code's wording). Participles that only describe a noun (*an application dated 12/10*, *a quotation amounting to*) are not acts unless they name a doer or the noun is the whole fragment (*Draft reply placed below for approval.*). *leave* is never an act, since office writing uses it as a noun (*Leave applications*), and neither is a verb used as part of a name (*the cleaning contractor*) or a present verb with no subject (*the admission register*). No model of RAM's own takes part in this step; spaCy's parser does.
2. **The reader only points** ([`ram/read.py`](ram/read.py)). An extractive MiniLM reader, fine-tuned for this job, reads the question with the writing and points at the span that does the act, or at nothing. When question and writing fit in 384 tokens it reads the whole writing, so a doer named in an earlier sentence is in view. Longer writing is read act by act, up to the end of the act's own sentence and back to the earliest sentence start that still fits. Only a single sentence longer than the reader takes is cut, from its start. The span is cut from the writer's own text by character offsets, so it cannot add a word or change a letter.
3. **Code decides whether the doer counts** ([`ram/kind.py`](ram/kind.py)). Code refuses doers that match its lists; any other doer counts. A leading *by* is dropped before the doer is judged, and so is anything from a *w.e.f.* or *vide* the span ran on into. Titles that name nobody (*the competent authority*, *the concerned department*, *this office*, *the management*, *the University Administration*, *it*, *they*, *we*) count as nobody, and so do phrases that are never somebody (*by speed post*, *by Friday*, *by the end of the month*, *14 October*, *Room 12*). Where a number stands decides what it is: after a reference word it is a reference (*Room 12*, *Section 12 of the Act*), before a unit of time it is a time (*14 October*, *12 noon*), with four digits it is refused, as years and rule numbers are (*GFR-2017*), and anywhere else it belongs to the post (*Lab Assistant 3*, *UDC-2*, *Ward 4 Inspector*). The lists are plain Python sets and patterns in `ram/kind.py`; edit them to change who counts.
4. **Code says it** ([`ram/__main__.py`](ram/__main__.py)), one line per act: the doer as the writer wrote it, with any leading article dropped, then *karega*; or *RAM bharose*.

The reader's no-answer margin is 0: it returns its best span whenever that span scores above the no-answer score. On the five test sets, every doerless act the reader pointed at anyway was refused by `kind.py`.

## How well it reads

`python tests/measure.py runs/ram-0.5 <set>`. Each set's key marks, for every act, the doer as written, *nobody*, or a title that names nobody (written with `~`), so `kind.py` is checked against a fixed answer and never against itself. The baseline is the parser alone: the grammatical subject of an active verb, or the *by* phrase of a passive one, put through the same `kind.py`.

| set | written by | acts | RAM 0.5 | parser alone |
|---|---|---|---|---|
| `notings.jsonl`: plain notings | Claude Code | 39 | **39** | 38 |
| `notings-hard.jsonl`: fragments, abbreviations, *the undersigned* | Claude Code | 35 | **35** | 32 |
| `notings-forms.jsonl`: forms found broken while preparing the release (fragments, numbered posts, bodies) | Claude Code | 24 | **24** | 20 |
| `notings-gemini.jsonl`: long university notings | Gemini 3 Flash, keyed by hand | 43 of 44 | **43** | 36 |
| `notings-gemini-2.jsonl`: hospital, bank, school, municipal | Gemini 3 Pro, keyed by hand | 37 | **37** | 36 |

Acts are the labelled acts the act finder finds: in `notings-gemini.jsonl` it misses one of 44 (*minutes placed opposite*), which is not scored.

**What these numbers do not show.**

- **Every set has been seen.** `notings.jsonl`, `notings-hard.jsonl` and the two Gemini sets were blind when first scored, and each then led to a fix, so none is a blind test any longer. The prompts used for the two Gemini sets are kept beside them (`tests/*.prompt.txt`), so a fresh set can be written the same way and keyed before RAM reads it.
- **On plain writing the parser alone does nearly as well.** Where each sentence says plainly who did what, the subject or *by* phrase is usually the doer. RAM is ahead on messier prose: recipients (*assigned to Shri Negi*), deciders (*submitted for orders of the Registrar*), a doer shared by joined verbs, a pronoun whose person was named earlier, and *by* phrases that are not doers (*by email*, *by speed post*).
- **All five sets were written by models.** RAM has not been measured on notings written by people.
- **`notings-forms.jsonl` was never blind.** It was written from forms that failed while the release was being prepared, each fixed in code or in the training rows; its full score shows only that those forms were fixed.
- **Long writing** is checked by `tests/test_long.py`: each of the 99 test notings is placed after, and before, about 530 tokens of references that name nobody, and every act must get the same answer as when the noting is read alone (both *RAM bharose*, or one doer containing the other). 0.5 does on all 99; 0.3, the reader before it, differed on 3: on two it took the doer of a neighbouring clause, and on one it missed, read alone, a doer it found beside the longer text.

**Known limits.**

- A fragment whose subject the parser tags as a name, and which is not on the list of papers, stays active: *Ravi received from the supplier* answers *Ravi karega*, as it should if Ravi did the receiving.
- *karega* is said for every doer (*I karega*, *Ms Joshi karega*); it does not follow person or gender.
- *we* is on the nobody list in `kind.py`.
- A section named for its work counts as somebody (*the Legal Department*, *the Library staff*); only a body ending in *Management* or *Administration* is refused whatever is in front of it.
- Nouns that stand for deeds (*approval is awaited*) are read only through a verb beside them.
- English only, in Roman letters.
- In long writing, a doer named after the act's sentence is never read, and one named earlier is read only if it falls inside the 384 tokens the question and the act's sentence leave room for (step 2).

## What RAM does not do

- Say why an act has no doer, or suggest who should do it.
- Rewrite a sentence, or write a word of its own.
- Show a score, a count or a percentage.
- Keep anything anybody types, or count who uses it.

## What RAM is not for

- Judging somebody else's writing.
- Any step in a decision about anybody. Its answer is meant for the person who wrote the sentence.

## Model, data and training

- **The reader** is deepset's [minilm-uncased-squad2](https://huggingface.co/deepset/minilm-uncased-squad2), fine-tuned on RAM's rows: 2 passes at learning rate 2e-5, batch 16, with three seeds (7, 1, 2) whose weights are averaged into one reader. About 155 seconds a seed on an NVIDIA GB10. [`MODEL-CARD.md`](MODEL-CARD.md)
- **The training data** ([`data/train-0.5.jsonl`](data/train-0.5.jsonl), 14,000 rows) is synthetic, with labels known by construction. [`scripts/synth.py`](scripts/synth.py) builds office notings from word lists in code: 25 given names and 24 family names from across India, posts, roles, sections named with and without *the*, titles that name nobody, twenty-three office acts, and the phrasing the reader has to handle (negated passives, joined verbs, relative clauses, *as confirmed by*, recipients after *to*, *for orders of*, noting fragments, lowercase typing with no full stop, and two clauses with their own subjects where only the first names a doer). About two notings in five are placed after one to three other notings, and, when they end in a full stop, before up to two more; only the placed noting's acts are labelled, so the doers of the others teach the reader what not to point at. Each act is asked the question `ram/acts.py` would ask, so the training questions are the questions RAM asks when it runs. The word lists and templates were written in Claude Code. No training sentence repeats a test sentence. Four names are shared: *Suresh*, *Sunita* and *Nair* in `notings-gemini.jsonl` and *Rao* in `notings-forms.jsonl` are also in the training name lists.
- **None of the training or test text names an animal product**; [`tests/test_vegan.py`](tests/test_vegan.py) scans the code, the data and the tests, and training runs only after it passes.

Reproduce the reader:

```bash
python tests/test_vegan.py
python scripts/synth.py --rows 14000 --seed 7 > data/train-0.5.jsonl
for s in 7 1 2; do python scripts/train.py --data data/train-0.5.jsonl --out runs/ram-0.5-s$s --seed $s; done
python scripts/train.py --soup runs/ram-0.5 runs/ram-0.5-s7 runs/ram-0.5-s1 runs/ram-0.5-s2
```

## Repository layout

```
ram/        the package: acts.py (finds the acts), read.py (the reader), kind.py (who counts), __main__.py (says it)
scripts/    synth.py (training data), train.py (training and weight averaging), check.sh (every check)
tests/      measure.py, test_kind.py, test_long.py, test_vegan.py, the five keyed test sets and the two prompts that wrote the Gemini sets
data/       train-0.5.jsonl, the 14,000 training rows
```

Run every check, with the reader in `runs/ram-0.5`:

```bash
bash scripts/check.sh      # the vegan scan, who counts, the leak guard, the reader on all five test sets, and long writing
```

## Licences and credit

- **Code:** GNU AGPL-3.0, in [`LICENSE`](LICENSE).
- **Weights and training data:** CC-BY-4.0, in [`LICENSE-WEIGHTS-AND-DATA.md`](LICENSE-WEIGHTS-AND-DATA.md).
- **Built on:** deepset's [minilm-uncased-squad2](https://huggingface.co/deepset/minilm-uncased-squad2) (CC-BY-4.0), Microsoft's [MiniLM](https://huggingface.co/microsoft/MiniLM-L12-H384-uncased) (MIT), and Explosion's [spaCy](https://spacy.io) and its [en_core_web_sm](https://huggingface.co/spacy/en_core_web_sm) model (MIT).
- **A sibling of [rai](https://github.com/koherarchitecture/rai)**, which uses the same reader base and the same split between pointing and deciding.
- **The idea:** the split between reading and deciding comes from [Split-Domain Cognition](https://splitdomaincognition.org), a principle that is nobody's property.

To cite RAM, see [`CITATION.cff`](CITATION.cff).

---

<p>
  RAM is made by <a href="https://koher.app">Koher</a>, which builds free AI tools that keep judgement in code anyone can read.
</p>
