# dataset/raw/

Put validated sign videos here, one folder per sign concept slug (matching
`sign_id`/`concept` in `backend/app/data/sign_metadata.csv`), one subfolder
per signer:

```
dataset/raw/
    help/
        signer_001/
            video_001.mp4
        signer_002/
            video_001.mp4
    pain/
        signer_001/
            ...
```

Do not add a folder here until the concept's source is recorded in
`DATASET_SOURCES.md` or it was collected via the in-app Dataset Collection
Mode with recorded consent. This directory is intentionally empty in the
delivered prototype — no fabricated or unverified sign videos are included.
