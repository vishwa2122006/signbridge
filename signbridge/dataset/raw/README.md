# dataset/raw/

Optional: sign videos to import with `ml/import_videos.py`. One folder per
word (a vocabulary concept slug, or `_none` for idle clips), one subfolder
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

Then, from the `signbridge/` folder:

```bash
backend/.venv/bin/python ml/import_videos.py --data_dir dataset/raw
```

See `ml/README.md` for flat layouts and mapping dataset folder names to
words. Only add videos you're allowed to use: record with consent and check
the licenses of downloaded datasets (see `DATASET_SOURCES.md`).
