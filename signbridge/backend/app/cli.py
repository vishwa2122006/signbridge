"""Database admin commands. Run from backend/ with the venv active:

    python -m app.cli init-db
    python -m app.cli create-user --role admin --name Vineeth --email someone@example.com
    python -m app.cli import-legacy

init-db       creates missing tables and adds the built-in words (the API also does this on start).
create-user   creates an admin or trainer with a verified email, or updates the account if the
              email exists. Asks for the password unless --password is given.
import-legacy moves recordings saved as files before the database existed
              (dataset/landmarks/<word>/*.json and dataset/custom_signs.csv) into the database,
              as approved recordings. Running it again skips what was already imported.
"""

import argparse
import csv
import getpass
import json
import os
import sys
from datetime import datetime, timezone
from typing import Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import config
from app.db import init_db, session_scope
from app.ml.features import DEFAULT_ASPECT
from app.models.tables import ADMIN, APPROVED, TRAINER, Sample, User, Word, utcnow
from app.services import sample_store
from app.services.security import hash_password
from app.services.vocabulary import vocabulary


def create_user(db: Session, *, name: str, email: str, password: str, role: str) -> Tuple[User, bool]:
    email = email.strip().lower()
    user = db.scalar(select(User).where(User.email == email))
    created = user is None
    if created:
        user = User(email=email)
        db.add(user)
    user.name, user.role, user.is_active = name.strip(), role, True
    user.password_hash = hash_password(password)
    user.email_verified_at = user.email_verified_at or utcnow()
    db.flush()
    return user, created


def import_legacy(db: Session) -> dict:
    words_added = 0
    path = config.legacy_custom_signs_path()
    if os.path.exists(path):  # custom words first, so their recordings have a word to belong to
        with open(path, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                if db.scalar(select(Word).where(Word.concept == row["concept"])) is not None:
                    continue
                db.add(Word(sign_id=row["sign_id"], concept=row["concept"], english=row["english"], tamil=row["tamil"],
                            category=row["category"], is_emergency=row["is_emergency"] == "yes", source="custom",
                            status=APPROVED))
                words_added += 1
        db.flush()

    imported, already, unknown = 0, 0, []
    root = config.legacy_samples_dir()
    existing = set(db.execute(select(Sample.signer_id, Sample.created_at)).tuples())
    for concept in sorted(os.listdir(root)) if os.path.isdir(root) else []:
        directory = os.path.join(root, concept)
        if not os.path.isdir(directory):
            continue
        word = None
        if concept != config.NONE_LABEL:
            word = db.scalar(select(Word).where(Word.concept == concept))
            if word is None:
                unknown.append(concept)
                continue
        for name in sorted(os.listdir(directory)):
            if not name.endswith(".json"):
                continue
            file_path = os.path.join(directory, name)
            with open(file_path, encoding="utf-8") as f:
                record = json.load(f)
            signer = record.get("signer_id") or "unknown"
            created = datetime.fromtimestamp(record.get("created_at") or os.path.getmtime(file_path), timezone.utc)
            if (signer, created) in existing:
                already += 1
                continue
            sample_store.save_sample(db, word, record["frames"], record.get("aspect") or DEFAULT_ASPECT,
                                     status=APPROVED, signer_id=signer, source=record.get("source") or "webcam",
                                     created_at=created)
            imported += 1
    return {"words_added": words_added, "imported": imported, "already_imported": already, "unknown_words": unknown}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init-db", help="create tables and add the built-in words")
    user_parser = commands.add_parser("create-user", help="create or update an admin or trainer")
    user_parser.add_argument("--role", choices=[ADMIN, TRAINER], required=True)
    user_parser.add_argument("--name", required=True)
    user_parser.add_argument("--email", required=True)
    user_parser.add_argument("--password", help="asked for if not given")
    commands.add_parser("import-legacy", help="move file-based recordings into the database")
    args = parser.parse_args()

    init_db()
    if args.command == "init-db":
        print(f"Database ready: {len(vocabulary.list_all())} approved words.")
    elif args.command == "create-user":
        password = args.password or getpass.getpass("Password: ")
        if not args.password and getpass.getpass("Repeat password: ") != password:
            sys.exit("Passwords don't match.")
        if len(password) < 6:
            sys.exit("The password needs at least 6 characters.")
        with session_scope() as db:
            user, created = create_user(db, name=args.name, email=args.email, password=password, role=args.role)
            print(f"{'Created' if created else 'Updated'} {user.role} {user.name} <{user.email}>")
    elif args.command == "import-legacy":
        with session_scope() as db:
            result = import_legacy(db)
        vocabulary.reload()
        print(f"Imported {result['imported']} recordings ({result['already_imported']} were already imported), "
              f"added {result['words_added']} custom words.")
        if result["unknown_words"]:
            print(f"Skipped folders that aren't vocabulary words: {', '.join(result['unknown_words'])}")


if __name__ == "__main__":
    main()
