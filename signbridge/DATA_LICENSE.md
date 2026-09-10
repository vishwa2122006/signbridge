# DATA_LICENSE.md — SignBridge

## External datasets

Every external dataset considered for this project is logged in
`DATASET_SOURCES.md` with its category (verified / research-reference /
not-suitable), and — once actually downloaded — its license terms should
be recorded there too, replacing any `UNVERIFIED` placeholder.

**Rule: never scrape, redistribute, or bundle a copyrighted video dataset
without confirmed permission.** This repository does not bundle any
third-party video files — `dataset/raw/` ships empty (see its README) so
that only data you've confirmed you're allowed to use gets added.

If a dataset's license is unclear or restrictive:
- Do not redistribute it as part of this project's deliverables (demo day
  submission, GitHub repo, etc.) unless the license explicitly allows it.
- You may still train a private model on it for the hackathon demo if the
  license allows non-commercial/research use, but say so explicitly in
  your presentation rather than implying the data is yours or freely
  redistributable.
- When in doubt, attribute the source and link to the original rather than
  copying files into this repo.

## Community-collected samples (Dataset Collection Mode)

For every sample collected through the app's Dataset Collection Mode:

- **Consent is mandatory and structural.** The backend
  (`feedback_store.record_dataset_sample`) refuses to log a sample without
  `consent_confirmed=true`; the frontend disables recording entirely until
  the consent checkbox is checked.
- **Signer IDs are anonymized handles** (e.g. `signer_03`), not real names.
  Don't repurpose them to store personally identifying information.
- **Explain the purpose** to each contributor before recording: what the
  clip will be used for (training a sign-recognition prototype), who will
  see it, and that participation is voluntary.
- **Allow withdrawal where feasible** — if a contributor asks to have
  their samples removed, remove their `signer_id`'s folder from
  `dataset/raw/` and their entries from `dataset_collection_log.jsonl`.
- **Don't collect unnecessary personal information.** The schema
  (`samples.csv` / the `/dataset/sample` endpoint) intentionally has no
  fields for name, contact info, or any identifier beyond an anonymized
  signer ID.

## Attribution

When you do confirm and use a Category B (or promoted Category A) dataset
from `DATASET_SOURCES.md`, credit it explicitly in your hackathon
submission/presentation — both because it's the right thing to do and
because judges will find "we built on X, here's what we added" more
credible than an unattributed claim of originality.
