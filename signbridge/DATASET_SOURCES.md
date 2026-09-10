# DATASET_SOURCES.md — SignBridge Dataset Audit

This audit was compiled from web research (search results and public listing
pages) during hackathon planning. **None of these sources have been
downloaded, manually inspected, or reviewed by a Tamil Sign Language
interpreter or Deaf-community validator as part of this audit.** Fields
marked `UNVERIFIED` mean exactly that — they were not confirmed
first-hand and must not be presented to judges or users as confirmed facts.

**Hard rule enforced by this document:** nothing in Category C may be used
to train, label, or claim a Tamil Sign Language sign. General Indian Sign
Language (ISL) data is useful only for pipeline engineering (testing your
landmark-extraction and classifier code), never as ground truth for what a
Tamil regional sign looks like.

---

## Category A — VERIFIED / HIGH CONFIDENCE

**None.** As of this audit, no dataset has been downloaded and manually
confirmed (license read in full, sample videos reviewed, signer count
checked, and — critically — content reviewed by someone who actually knows
Tamil Nadu regional sign language) to belong in this category. This is
intentional and should stay this way until real verification happens —
do not move anything into Category A based on a filename or a dataset
listing's title alone.

**Action before the hackathon (or in its first hour):** pick the top 1-2
candidates from Category B below, download them, and actually check: does
the license permit hackathon/derivative use? Do the sample videos look like
real, distinct signs performed by more than one signer? Is there any
statement of who validated them? Only then promote an entry to Category A.

---

## Category B — RESEARCH REFERENCE / NEEDS VALIDATION

These explicitly claim to be Tamil Sign Language (not generic ISL), so
they are the right starting point — but every field below needs direct
confirmation before you rely on them for anything shown to a judge as fact.

### 1. Tamil Sign Language Video Dataset (Kaggle)
- **URL:** https://www.kaggle.com/datasets/s3programmerlead/tamil-sign-language-video-dataset
- **Organization/person:** Kaggle user `s3programmerlead` — UNVERIFIED whether an individual hobbyist, student, or institution
- **Language/sign system:** Claims "Tamil Sign Language" — UNVERIFIED whether this reflects Tamil-Nadu-regional Deaf-community usage or an author's own interpretation
- **Number of classes:** UNVERIFIED — check the Kaggle listing/metadata directly
- **Number of samples/videos:** UNVERIFIED
- **Number of signers:** UNVERIFIED — critical field, since a single-signer dataset cannot support a signer-held-out validation split
- **Format:** Video (per title) — exact codec/resolution UNVERIFIED
- **License:** UNVERIFIED — read the Kaggle dataset's license tab before any use
- **Commercial use allowed:** UNVERIFIED
- **Redistribution allowed:** UNVERIFIED
- **Is it actually Tamil Sign Language:** Claimed, not independently confirmed
- **Is it ISL:** No claim of this
- **Fingerspelling-only:** UNVERIFIED — check whether classes are alphabet letters or whole concepts/words
- **Suitable for healthcare vocabulary:** UNVERIFIED — depends entirely on which classes it contains; do not assume it covers "pain," "help," etc.
- **Confidence/validation level:** Research-reference only
- **Limitations:** No stated Deaf-community validation found during this audit; single unverified contributor

### 2. TLFS23 — Tamil Language Fingerspelling Dataset (ScienceDirect data descriptor)
- **URL:** https://www.sciencedirect.com/science/article/pii/S2352340923009927
- **Organization/person:** Published as a peer-reviewed data descriptor — authors UNVERIFIED without opening the paper
- **Language/sign system:** Tamil **fingerspelling** specifically (per title)
- **Number of classes / samples / signers:** UNVERIFIED — read the paper's methods section
- **Format:** UNVERIFIED
- **License:** ScienceDirect data descriptors are typically CC-BY or similar, but the exact license must be confirmed on the article page — do not assume
- **Commercial use / redistribution allowed:** UNVERIFIED
- **Is it actually Tamil Sign Language:** It is Tamil fingerspelling (letter-by-letter spelling), which is a *component* of sign communication, not the same as whole-concept signs like "pain" or "help"
- **Fingerspelling-only:** Yes, by its own title
- **Suitable for healthcare vocabulary:** Only indirectly — fingerspelling could be a fallback for names/unlisted words, not a substitute for validated concept-signs
- **Confidence/validation level:** Research-reference (peer-reviewed, which is a positive signal, but still unverified by this audit directly)
- **Limitations:** Being peer-reviewed does not by itself confirm Tamil-Nadu regional/Deaf-community validation — check the paper's own validation methodology

### 3. Glossia (IEEE DataPort)
- **URL:** https://ieee-dataport.org/documents/glossia-0
- **Organization/person:** UNVERIFIED — requires an IEEE DataPort account to view full details
- **Language/sign system:** Listed under Tamil sign language search results; not independently confirmed
- **All other fields:** UNVERIFIED — IEEE DataPort often requires a free account or request/approval before full metadata and download access are visible
- **Confidence/validation level:** Research-reference only, lowest confidence of the three Tamil-labeled sources because even basic metadata wasn't accessible during this audit
- **Limitations:** Access friction (account/approval) means don't count on this as your primary source under hackathon time pressure

### 4. Velogan-Boy / sign-language-recognition (GitHub)
- **URL:** https://github.com/Velogan-Boy/sign-language-recognition
- **Organization/person:** Individual GitHub contributor — UNVERIFIED credentials or Deaf-community involvement
- **Language/sign system:** Titled "Tamil Isolated Sign Language Recognition"
- **Number of classes/samples/signers:** UNVERIFIED — open the repo and check whether training data is bundled or only code
- **Format:** Likely code + possibly a small bundled dataset — UNVERIFIED
- **License:** Check the repo's LICENSE file directly (GitHub repos without one default to "all rights reserved" — do not assume MIT/permissive)
- **Commercial use / redistribution allowed:** UNVERIFIED — depends on the license file
- **Is it actually Tamil Sign Language:** Claimed by repo title, not independently validated
- **Suitable for healthcare vocabulary:** UNVERIFIED — likely a small alphabet/word demo set, not healthcare-scoped
- **Confidence/validation level:** Research/code reference — most useful as an architecture reference (how someone else structured the MediaPipe pipeline), not as a guaranteed data source
- **Limitations:** Hobby-scale project; no evidence found of community validation

---

## Category C — NOT SUITABLE FOR CLAIMING TAMIL SIGN LANGUAGE

These are real, useful datasets — but they are **general Indian Sign
Language (ISL) or unrelated to Tamil sign language entirely**. Per the
explicit project rule: never relabel these as Tamil Sign Language, and
never train a class called "Tamil sign for X" directly from these. They
are listed here because they are legitimately useful for **pipeline
engineering** — testing your landmark-extraction code, prototyping your
classifier architecture, sanity-checking your training loop — before you
have your own validated Tamil data ready.

- **Indian Sign Language words with Landmarks (Kaggle)** — https://www.kaggle.com/datasets/kaushikyh/indian-sign-language-words-with-landmarks/data — ISL, pre-extracted landmarks. Good for pipeline testing only.
- **Indian Sign Language Hand Landmarks Dataset (Kaggle)** — https://www.kaggle.com/datasets/eraakash/indian-sign-language-hand-landmarks-dataset — ISL, pre-extracted landmarks. Pipeline testing only.
- **Indian Sign Language_Dataset (Mendeley)** — https://data.mendeley.com/datasets/yx7kdssfjp/1 — ISL. Not Tamil-specific.
- **ISLVT — Indian Sign Language Video and Text dataset for sentences (Mendeley)** — https://data.mendeley.com/datasets/98mzk82wbb/1 — ISL, continuous/sentence-level. Not isolated-sign, not Tamil-specific.
- **Exploration-Lab/iSign (Hugging Face)** — https://huggingface.co/datasets/Exploration-Lab/iSign — large ISL benchmark, continuous signing. Not Tamil-specific; also a data format mismatch for an isolated-sign MVP.
- **imRishabhGupta/Indian-Sign-Language-Recognition (GitHub)** — https://github.com/imRishabhGupta/Indian-Sign-Language-Recognition — general ISL alphabet recognition code. Reference for architecture only.

**Also explicitly out of scope:** any dataset whose filename or title
contains "Tamil" but which, on inspection, turns out to be Tamil-*language
text/speech* data (translation corpora, TTS/ASR datasets like the Tamil
Whisper/wav2vec2 models found during research) — those are about the
*spoken/written* Tamil language, not Tamil *Sign* Language, and must never
be conflated.

---

## Required next step before training on anything in Category B

1. Download the dataset (start with the Kaggle Tamil Sign Language Video
   Dataset — lowest access friction).
2. Read its license in full; record the actual terms here, replacing the
   `UNVERIFIED` fields above.
3. If at all possible, get even one Tamil Nadu Deaf-community member,
   interpreter, or special-education teacher to look at a sample of the
   videos and confirm: "yes, this is a sign I recognize," or "no, this
   isn't how we sign this." Record their response in `sign_metadata.csv`
   under `validation_status`.
4. Only signs with at least research-reference-level sourcing go into the
   demo. Anything without a traceable source is excluded, not guessed.

## Importing a checked dataset

Once a dataset passes the checks above, arrange (or map) its videos by word
and import them as training samples. They mix with samples recorded on the
Teach Signs page:

```bash
backend/.venv/bin/python ml/import_videos.py --data_dir <videos> [--flat --signer NAME] [--map map.csv]
backend/.venv/bin/python ml/train.py
```

See `ml/README.md` for the folder layouts and the mapping CSV format.
