"""The emails SignBridge sends: plain text plus a designed HTML version.

Registration and login codes are sent while the request waits, so a failure
can be shown. Notifications about sign-ups, submissions and reviews run as
FastAPI background tasks after the response, and a failure is only logged.
Those tasks get plain values (Person, labels, counts), never database
objects, because the request's database session is closed by the time they run.

The HTML sticks to tables and inline styles, which is what email clients
(Gmail, Outlook, phone mail apps) render reliably. Every piece of text that
comes from users is escaped.
"""

from dataclasses import dataclass
from html import escape as esc
from typing import List, Optional, Sequence, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import config
from app.models.tables import ADMIN, APPROVED, User, Word
from app.services import mailer

IDLE_LABEL = "Idle (no sign)"
IDLE_LABEL_TA = "ஓய்வு (சைகை இல்லை)"

BACKGROUND_LABELS = {
    "deaf": "Deaf signer",
    "hard_of_hearing": "Hard of hearing",
    "interpreter": "Sign language interpreter",
    "teacher": "Teacher of Deaf students",
    "family": "Family member or friend of a Deaf person",
    "student": "Student / learner",
    "other": "Other",
}
SIGNING_LEVEL_LABELS = {"native": "Native signer", "fluent": "Fluent", "intermediate": "Intermediate", "beginner": "Beginner"}
SIGN_LANGUAGE_LABELS = {
    "tamil": "Tamil Sign Language",
    "indian": "Indian Sign Language (ISL)",
    "both": "Tamil and Indian Sign Language",
    "other": "Other",
}

Counts = Sequence[Tuple[str, int]]  # (word label, number of recordings)

TRAINER_FOOTER = "You're receiving this email because you are a SignBridge trainer."
ADMIN_FOOTER = "You're receiving this email because you are a SignBridge admin."
CODE_FOOTER = "You're receiving this email because this address was entered on SignBridge."


@dataclass(frozen=True)
class Person:
    name: str
    email: str


def person(user: User) -> Person:
    return Person(user.name, user.email)


def admin_emails(db: Session) -> List[str]:
    return list(db.scalars(select(User.email).where(User.role == ADMIN, User.is_active.is_(True)).order_by(User.id)))


def word_label(word: Optional[Word]) -> str:
    """How a word is named in emails ("English / Tamil"); None is the Idle class."""
    return f"{word.english} / {word.tamil}" if word is not None else IDLE_LABEL


def registration_details(user: User) -> List[Tuple[str, str]]:
    rows = [
        ("Phone", user.phone),
        ("City", user.city),
        ("Organization", user.organization),
        ("Background", BACKGROUND_LABELS.get(user.background, user.background)),
        ("Signing level", SIGNING_LEVEL_LABELS.get(user.signing_level, user.signing_level)),
        ("Sign language", SIGN_LANGUAGE_LABELS.get(user.sign_language, user.sign_language)),
        ("About", user.about),
    ]
    return [(label, value) for label, value in rows if value]


# ---------- design ----------

@dataclass(frozen=True)
class Theme:
    color: str  # badge, numbers, button (dark enough for white button text)
    tint: str  # light background behind the icon, badge, chips and note
    icon: str


THEMES = {
    "code": Theme("#6d28d9", "#f1ebff", "🔐"),
    "welcome": Theme("#0f766e", "#dcfaf4", "🎉"),
    "trainer": Theme("#0369a1", "#e0f2fe", "👋"),
    "submitted": Theme("#b45309", "#fef3c7", "📤"),
    "word": Theme("#be185d", "#fce7f3", "🆕"),
    "review": Theme("#6d28d9", "#f1ebff", "📋"),
    "approved": Theme("#15803d", "#dcfce7", "✅"),
    "rejected": Theme("#b91c1c", "#fee2e2", "🔁"),
    "deleted": Theme("#475569", "#e2e8f0", "🗑️"),
}

_FONT = "'Segoe UI',Roboto,'Noto Sans Tamil','Noto Sans',Helvetica,Arial,sans-serif"
_INK = "#1b1640"
_BODY = "#3f3a5a"
_MUTED = "#6b6790"
_TABLE = 'role="presentation" cellspacing="0" cellpadding="0" border="0"'


@dataclass(frozen=True)
class Row:
    """A line in a list: a word with its Tamil and a count chip, or a numbered step."""
    title: str
    subtitle: str = ""
    chip: str = ""
    chip_theme: str = ""  # defaults to the email's theme
    step: str = ""


@dataclass(frozen=True)
class Email:
    theme: str
    badge: str
    title: str
    title_ta: str
    preheader: str  # the grey preview line in the inbox
    footer: str
    greeting: str = ""
    intro: Sequence[str] = ()
    code: str = ""
    stats: Sequence[Tuple[int, str, str]] = ()  # (number, label, theme)
    rows: Sequence[Row] = ()
    details: Sequence[Tuple[str, str]] = ()
    note: Optional[Tuple[str, str]] = None  # (label, text)
    outro: Sequence[str] = ()
    action: Optional[Tuple[str, str]] = None  # (label, url)

    def text(self) -> str:
        parts = [f"{self.title}\n{self.title_ta}"]
        if self.greeting:
            parts.append(self.greeting)
        parts.extend(self.intro)
        if self.code:
            parts.append(self.code)
        if self.stats:
            parts.append("   ".join(f"{n} {label.lower()}" for n, label, _ in self.stats))
        if self.rows:
            parts.append("\n".join(
                f"  {row.step + '.' if row.step else '-'} {row.title}"
                + (f" / {row.subtitle}" if row.subtitle else "") + (f"  [{row.chip}]" if row.chip else "")
                for row in self.rows
            ))
        if self.details:
            parts.append("\n".join(f"  {label}: {value}" for label, value in self.details))
        if self.note:
            parts.append(f"{self.note[0]}: {self.note[1]}")
        parts.extend(self.outro)
        if self.action:
            parts.append(f"{self.action[0]}: {self.action[1]}")
        parts.append(f"- SignBridge\n{self.footer}")
        return "\n\n".join(parts)

    def html(self) -> str:
        theme = THEMES[self.theme]
        blocks = []
        if self.greeting:
            blocks.append(_paragraph(self.greeting, color=_INK, weight=700))
        blocks.extend(_paragraph(p) for p in self.intro)
        if self.code:
            blocks.append(_code(self.code, theme))
        if self.stats:
            blocks.append(_stats(self.stats))
        if self.rows:
            blocks.append(_rows(self.rows, theme))
        if self.details:
            blocks.append(_details(self.details))
        if self.note:
            blocks.append(_note(*self.note, theme))
        blocks.extend(_paragraph(p, color=_MUTED, size=14) for p in self.outro)
        if self.action:
            blocks.append(_button(*self.action, theme))

        return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light only"><meta name="supported-color-schemes" content="light">
<title>{esc(self.title)}</title></head>
<body style="margin:0;padding:0;background:#f1edff;">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;mso-hide:all;">{esc(self.preheader)}</div>
<table {_TABLE} width="100%" style="background:#f1edff;"><tr><td align="center" style="padding:28px 12px;font-family:{_FONT};">
<table {_TABLE} width="100%" style="max-width:600px;background:#ffffff;border-radius:22px;overflow:hidden;box-shadow:0 14px 40px rgba(76,29,149,0.14);">
<tr><td style="padding:20px 28px;background-color:#8b5cf6;background-image:linear-gradient(120deg,#ff4f9a 0%,#8b5cf6 55%,#2ee6c5 100%);">
  <table {_TABLE}><tr>
    <td width="46" height="46" align="center" style="width:46px;height:46px;border-radius:14px;background:rgba(255,255,255,0.24);font-size:26px;line-height:46px;">🤟</td>
    <td style="padding-left:14px;font-family:{_FONT};color:#ffffff;">
      <div style="font-size:22px;line-height:1.2;font-weight:800;letter-spacing:0.3px;">SignBridge</div>
      <div style="font-size:12px;line-height:1.5;color:#fdf4ff;">Sign language to Tamil &amp; English · சைகை மொழி → தமிழ் &amp; ஆங்கிலம்</div>
    </td>
  </tr></table>
</td></tr>
<tr><td align="center" style="padding:34px 32px 4px;font-family:{_FONT};">
  <table {_TABLE} align="center"><tr><td width="76" height="76" align="center" style="width:76px;height:76px;border-radius:38px;background:{theme.tint};font-size:36px;line-height:76px;">{theme.icon}</td></tr></table>
  <div style="margin-top:16px;"><span style="display:inline-block;padding:5px 14px;border-radius:999px;background:{theme.tint};color:{theme.color};font-size:11px;font-weight:800;letter-spacing:1px;text-transform:uppercase;">{esc(self.badge)}</span></div>
  <h1 style="margin:14px 0 6px;font-family:{_FONT};font-size:25px;line-height:1.3;font-weight:800;color:{_INK};">{esc(self.title)}</h1>
  <div style="font-size:15px;line-height:1.5;font-weight:600;color:{theme.color};">{esc(self.title_ta)}</div>
</td></tr>
<tr><td style="padding:24px 36px 34px;font-family:{_FONT};">{"".join(blocks)}</td></tr>
</table>
<table {_TABLE} width="100%" style="max-width:600px;"><tr><td align="center" style="padding:18px 24px 4px;font-family:{_FONT};font-size:12px;line-height:1.7;color:#8a85a6;">
  {esc(self.footer)}<br>
  <a href="{esc(config.FRONTEND_URL)}" style="color:#6d28d9;font-weight:700;text-decoration:none;">Open SignBridge</a> · A communication aid, not a certified interpreter or medical advice.<br>
  <span style="color:#ff4f9a;">&#9829;</span> Helping Deaf people be understood in Tamil and English
</td></tr></table>
</td></tr></table>
</body></html>"""


def _paragraph(text: str, color: str = _BODY, size: int = 15, weight: int = 400) -> str:
    return f'<p style="margin:0 0 14px;font-size:{size}px;line-height:1.6;font-weight:{weight};color:{color};">{esc(text)}</p>'


def _code(code: str, theme: Theme) -> str:
    size = 36 if len(code) <= 6 else 26  # fits a 360px-wide phone screen
    cells = "".join(
        f'<td style="padding:0 2px;"><div style="width:{size}px;height:{size + 12}px;line-height:{size + 12}px;'
        f"border-radius:12px;background:{theme.tint};border:2px solid {theme.color};text-align:center;"
        f"font-family:'Courier New',Courier,monospace;font-size:{size // 2 + 6}px;font-weight:700;color:{_INK};\">"
        f"{esc(digit)}</div></td>"
        for digit in code
    )
    return (
        f'<table {_TABLE} align="center" style="margin:10px auto 10px;"><tr>{cells}</tr></table>'
        f'<p style="margin:0 0 20px;text-align:center;font-size:12px;color:{_MUTED};">Copy: '
        f"<span style=\"font-family:'Courier New',Courier,monospace;font-size:14px;font-weight:700;letter-spacing:3px;color:{_INK};\">"
        f"{esc(code)}</span></p>"
    )


def _stats(stats: Sequence[Tuple[int, str, str]]) -> str:
    width = 100 // len(stats)
    cells = "".join(
        f'<td width="{width}%" style="padding:4px;"><div style="padding:14px 6px;border-radius:14px;text-align:center;background:{THEMES[t].tint};">'
        f'<div style="font-size:30px;line-height:1.1;font-weight:800;color:{THEMES[t].color};">{n}</div>'
        f'<div style="margin-top:3px;font-size:11px;font-weight:800;letter-spacing:0.8px;text-transform:uppercase;color:{THEMES[t].color};">{esc(label)}</div>'
        "</div></td>"
        for n, label, t in stats
    )
    return f'<table {_TABLE} width="100%" style="margin:2px 0 16px;"><tr>{cells}</tr></table>'


def _rows(rows: Sequence[Row], theme: Theme) -> str:
    lines = []
    for i, row in enumerate(rows):
        border = "" if i == 0 else "border-top:1px solid #efecfa;"
        chip_theme = THEMES.get(row.chip_theme, theme)
        step = (
            f'<td width="46" valign="top" style="padding:13px 0 13px 16px;{border}">'
            f'<div style="width:30px;height:30px;line-height:30px;border-radius:15px;background:{theme.color};color:#ffffff;'
            f'text-align:center;font-size:14px;font-weight:800;">{esc(row.step)}</div></td>'
        ) if row.step else ""
        subtitle = (
            f'<div style="margin-top:2px;font-size:13px;line-height:1.5;color:{_MUTED};">{esc(row.subtitle)}</div>'
        ) if row.subtitle else ""
        chip = (
            f'<td align="right" valign="middle" style="padding:12px 16px;{border}">'
            f'<span style="display:inline-block;padding:4px 11px;border-radius:999px;background:{chip_theme.tint};'
            f'color:{chip_theme.color};font-size:12px;font-weight:800;white-space:nowrap;">{esc(row.chip)}</span></td>'
        ) if row.chip else ""
        lines.append(
            f"<tr>{step}"
            f'<td valign="middle" style="padding:12px 16px;{border}"><div style="font-size:15px;line-height:1.4;font-weight:700;color:{_INK};">'
            f"{esc(row.title)}</div>{subtitle}</td>{chip}</tr>"
        )
    return (
        f'<table {_TABLE} width="100%" style="margin:4px 0 18px;border:1px solid #e7e3f8;border-radius:14px;'
        f'border-collapse:separate;">{"".join(lines)}</table>'
    )


def _details(pairs: Sequence[Tuple[str, str]]) -> str:
    lines = "".join(
        f'<tr><td valign="top" width="36%" style="padding:8px 16px;font-size:13px;line-height:1.5;color:{_MUTED};">{esc(label)}</td>'
        f'<td style="padding:8px 16px;font-size:14px;line-height:1.5;font-weight:600;color:{_INK};">{esc(value)}</td></tr>'
        for label, value in pairs
    )
    return f'<table {_TABLE} width="100%" style="margin:4px 0 18px;background:#faf8ff;border-radius:14px;">{lines}</table>'


def _note(label: str, text: str, theme: Theme) -> str:
    return (
        f'<table {_TABLE} width="100%" style="margin:2px 0 18px;"><tr>'
        f'<td style="padding:14px 18px;background:{theme.tint};border-left:4px solid {theme.color};border-radius:0 12px 12px 0;">'
        f'<div style="font-size:11px;font-weight:800;letter-spacing:0.8px;text-transform:uppercase;color:{theme.color};">{esc(label)}</div>'
        f'<div style="margin-top:4px;font-size:15px;line-height:1.5;color:{_INK};">“{esc(text)}”</div></td></tr></table>'
    )


def _button(label: str, url: str, theme: Theme) -> str:
    return (
        f'<table {_TABLE} align="center" style="margin:24px auto 4px;"><tr>'
        f'<td align="center" bgcolor="{theme.color}" style="border-radius:999px;background:{theme.color};">'
        f'<a href="{esc(url)}" style="display:inline-block;padding:14px 34px;border-radius:999px;font-family:{_FONT};'
        f'font-size:15px;font-weight:700;color:#ffffff;text-decoration:none;">{esc(label)} &rarr;</a></td></tr></table>'
    )


# ---------- helpers ----------

def _link(path: str) -> str:
    return f"{config.FRONTEND_URL}/#{path}"


def _plural(n: int, noun: str) -> str:
    return f"{n} {noun}{'' if n == 1 else 's'}"


def _total(counts: Counts) -> int:
    return sum(n for _, n in counts)


def _word(label: str) -> Tuple[str, str]:
    """(English, Tamil) from a word label."""
    if label == IDLE_LABEL:
        return IDLE_LABEL, IDLE_LABEL_TA
    english, _, tamil = label.partition(" / ")
    return english, tamil


def _word_rows(counts: Counts, symbol: str, chip_theme: str = "") -> List[Row]:
    return [Row(*_word(label), chip=f"{symbol} {n}", chip_theme=chip_theme) for label, n in counts]


def _send(to: Sequence[str], subject: str, message: Email, quietly: bool = True):
    send = mailer.send_quietly if quietly else mailer.send
    send(to, subject, message.text(), message.html())


# ---------- the emails ----------

def send_code(name: str, email: str, code: str, purpose: str):
    """Raises mailer.EmailError if the email can't be sent."""
    registering = purpose == "register"
    minutes = _plural(config.OTP_EXPIRE_MINUTES, "minute")
    _send([email], f"{code} is your SignBridge code", Email(
        theme="code",
        badge="Confirm your email" if registering else "Login code",
        title="Your verification code" if registering else "Your login code",
        title_ta="உங்கள் சரிபார்ப்புக் குறியீடு" if registering else "உங்கள் உள்நுழைவுக் குறியீடு",
        preheader=f"{code} is your SignBridge code. It expires in {minutes}.",
        greeting=f"Hi {name},",
        intro=["Enter this code to finish signing up as a SignBridge trainer:" if registering
               else "Enter this code to log in to SignBridge:"],
        code=code,
        outro=[f"The code expires in {minutes}. Never share it with anyone.",
               "Didn't ask for this? You can safely ignore this email."],
        footer=CODE_FOOTER,
    ), quietly=False)


def trainer_registered(trainer: Person, details: Sequence[Tuple[str, str]], admins: List[str]):
    """Sign-up complete: a welcome for the new trainer and a notice with their details for the admins."""
    _send([trainer.email], "Welcome to SignBridge", Email(
        theme="welcome",
        badge="Welcome aboard",
        title="You're now a SignBridge trainer!",
        title_ta="நீங்கள் இப்போது SignBridge பயிற்சியாளர்!",
        preheader="Your sign-up is complete. Here's how to start teaching SignBridge.",
        greeting=f"Hi {trainer.name},",
        intro=["Your sign-up is complete. Thank you for helping Deaf people be understood in Tamil and English! "
               "Here's how it works:"],
        rows=[
            Row("Record signs", "Pick a word on Teach Signs and record it a few times. "
                                "Only hand and body points are saved, never video.", step="1"),
            Row("Submit for review", "Your recordings stay private drafts until you submit them.", step="2"),
            Row("Get approved", "An admin checks every recording, and you'll get an email with the result.", step="3"),
            Row("Grow the vocabulary", "Missing a word? Propose it with its English and Tamil text.", step="4"),
        ],
        action=("Start recording", _link("/teach")),
        footer=TRAINER_FOOTER,
    ))
    _send(admins, f"New trainer registered: {trainer.name}", Email(
        theme="trainer",
        badge="New sign-up",
        title=f"{trainer.name} joined as a trainer",
        title_ta="புதிய பயிற்சியாளர் இணைந்துள்ளார்",
        preheader=f"{trainer.name} ({trainer.email}) signed up and verified their email.",
        intro=[f"{trainer.name} signed up and verified their email address. Their details:"],
        details=[("Name", trainer.name), ("Email", trainer.email), *details],
        outro=["If this account shouldn't be here, you can disable it on the Trainers tab."],
        action=("See trainers", _link("/review?tab=trainers")),
        footer=ADMIN_FOOTER,
    ))


def samples_submitted(trainer: Person, counts: Counts, admins: List[str]):
    total = _plural(_total(counts), "recording")
    rows = _word_rows(counts, "×")
    _send(admins, f"Review needed: {total} from {trainer.name}", Email(
        theme="submitted",
        badge="Review needed",
        title=f"{total} waiting for review",
        title_ta="சரிபார்ப்புக்குப் புதிய பதிவுகள் காத்திருக்கின்றன",
        preheader=f"{trainer.name} submitted {total} for {_plural(len(counts), 'word')}.",
        intro=[f"{trainer.name} ({trainer.email}) submitted {total} for review:"],
        rows=rows,
        action=("Review recordings", _link("/review")),
        footer=ADMIN_FOOTER,
    ))
    _send([trainer.email], f"Submitted for review: {total}", Email(
        theme="submitted",
        badge="Submitted",
        title="Your recordings are in review",
        title_ta="உங்கள் பதிவுகள் சரிபார்ப்பில் உள்ளன",
        preheader=f"Thank you! Your {total} went to the admin for review.",
        greeting=f"Hi {trainer.name},",
        intro=[f"Thank you! Your {total} went to the admin for review:"],
        rows=rows,
        outro=["You'll get an email as soon as they're approved or rejected."],
        action=("See my recordings", _link("/teach")),
        footer=TRAINER_FOOTER,
    ))


def word_proposed(trainer: Person, label: str, admins: List[str]):
    english, tamil = _word(label)
    rows = [Row(english, tamil, chip="Waiting", chip_theme="submitted")]
    _send(admins, f"New word proposed: {label}", Email(
        theme="word",
        badge="New word",
        title=f"New word proposed: {english}",
        title_ta="புதிய சொல் பரிந்துரைக்கப்பட்டுள்ளது",
        preheader=f"{trainer.name} proposed “{english}” for the vocabulary.",
        intro=[f"{trainer.name} ({trainer.email}) proposed a new word for the vocabulary:"],
        rows=rows,
        outro=["Check the English and Tamil text (you can correct it) - the word joins the vocabulary once you approve it."],
        action=("Review the word", _link("/review")),
        footer=ADMIN_FOOTER,
    ))
    _send([trainer.email], f"Word sent for review: {label}", Email(
        theme="word",
        badge="Sent for approval",
        title="Your new word is waiting for approval",
        title_ta="உங்கள் புதிய சொல் ஒப்புதலுக்குக் காத்திருக்கிறது",
        preheader=f"“{english}” went to the admin for approval.",
        greeting=f"Hi {trainer.name},",
        intro=["Thanks for growing the vocabulary! Your word went to the admin:"],
        rows=rows,
        outro=["You can record it already: its recordings can be approved once the word is. "
               "We'll email you when it's reviewed."],
        action=("Record it now", _link("/teach")),
        footer=TRAINER_FOOTER,
    ))


def samples_reviewed(trainer: Person, reviewer: str, approved: Counts, rejected: Counts, note: Optional[str]):
    n_approved, n_rejected = _total(approved), _total(rejected)
    summary = ", ".join(part for part, n in ((f"{n_approved} approved", n_approved), (f"{n_rejected} rejected", n_rejected)) if n)
    if not n_rejected:
        theme, title, title_ta = "approved", "Your recordings were approved", "உங்கள் பதிவுகள் ஏற்கப்பட்டன"
    elif not n_approved:
        theme, title, title_ta = "rejected", "Some recordings need another try", "சில பதிவுகளை மீண்டும் பதிவு செய்ய வேண்டும்"
    else:
        theme, title, title_ta = "review", "Your recordings were reviewed", "உங்கள் பதிவுகள் சரிபார்க்கப்பட்டன"
    outro = []
    if n_approved:
        outro.append("Approved recordings are used the next time the model is trained. Thank you!")
    if n_rejected:
        outro.append("You can record those words again and resubmit them.")
    _send([trainer.email], f"Your recordings were reviewed: {summary}", Email(
        theme=theme,
        badge="Review result",
        title=title,
        title_ta=title_ta,
        preheader=f"{reviewer} reviewed your recordings: {summary}.",
        greeting=f"Hi {trainer.name},",
        intro=[f"{reviewer} reviewed your recordings:"],
        stats=[(n, label, t) for n, label, t in ((n_approved, "Approved", "approved"), (n_rejected, "Rejected", "rejected")) if n],
        rows=_word_rows(approved, "✓", "approved") + _word_rows(rejected, "✕", "rejected"),
        note=("Note from the admin", note) if note and n_rejected else None,
        outro=outro,
        action=("See my recordings", _link("/teach")),
        footer=TRAINER_FOOTER,
    ))


def review_summary(reviewer: str, per_trainer: Sequence[Tuple[Person, int, int]], note: Optional[str], admins: List[str]):
    approved = sum(a for _, a, _ in per_trainer)
    rejected = sum(r for _, _, r in per_trainer)
    _send(admins, f"Review saved: {approved} approved, {rejected} rejected", Email(
        theme="review",
        badge="Review saved",
        title=f"{reviewer} reviewed {_plural(approved + rejected, 'recording')}",
        title_ta="சரிபார்ப்பு சேமிக்கப்பட்டது",
        preheader=f"{approved} approved, {rejected} rejected. The trainers were emailed their results.",
        intro=[f"Recordings from {_plural(len(per_trainer), 'trainer')} were reviewed, and each trainer was emailed their results:"],
        stats=[(approved, "Approved", "approved"), (rejected, "Rejected", "rejected")],
        rows=[Row(p.name, p.email, chip=f"✓ {a}   ✕ {r}") for p, a, r in per_trainer],
        note=("Note for the rejected recordings", note) if note and rejected else None,
        action=("Open Review & Train", _link("/review")),
        footer=ADMIN_FOOTER,
    ))


def recordings_deleted(reviewer: str, label: str, per_trainer: Sequence[Tuple[Person, int]], total: int,
                       admins: List[str]):
    english, tamil = _word(label)
    for trainer, count in per_trainer:
        _send([trainer.email], f"Recordings removed: {english}", Email(
            theme="deleted",
            badge="Recordings removed",
            title=f"Recordings of “{english}” were removed",
            title_ta="இந்தச் சொல்லின் பதிவுகள் நீக்கப்பட்டன",
            preheader=f"{reviewer} removed every recording of “{english}”, including {_plural(count, 'recording')} of yours.",
            greeting=f"Hi {trainer.name},",
            intro=[f"{reviewer} removed every recording of this word, including {_plural(count, 'recording')} of yours:"],
            rows=[Row(english, tamil, chip=f"🗑 {count}")],
            outro=["This usually means the word is being recorded again from scratch. You're welcome to record it again."],
            action=("Open Teach Signs", _link("/teach")),
            footer=TRAINER_FOOTER,
        ))
    _send(admins, f"Recordings deleted: {_plural(total, 'recording')} of {english}", Email(
        theme="deleted",
        badge="Recordings deleted",
        title=f"{reviewer} deleted {_plural(total, 'recording')}",
        title_ta="பதிவுகள் நீக்கப்பட்டன",
        preheader=f"Every recording of “{english}” was deleted.",
        intro=["Every recording of this word was deleted, from all trainers:"],
        rows=[Row(english, tamil, chip=f"🗑 {total}")],
        details=[(f"{p.name} ({p.email})", _plural(n, "recording")) for p, n in per_trainer],
        outro=["The trained model still knows these recordings until it's trained again."],
        action=("Open Review & Train", _link("/review")),
        footer=ADMIN_FOOTER,
    ))


def word_reviewed(proposer: Optional[Person], reviewer: str, label: str, status: str, note: Optional[str],
                  admins: List[str]):
    english, tamil = _word(label)
    approved = status == APPROVED
    verdict = "approved" if approved else "rejected"
    theme = "approved" if approved else "rejected"
    rows = [Row(english, tamil, chip="Approved" if approved else "Not approved", chip_theme=theme)]
    note_block = ("Note from the admin", note) if note else None
    if proposer is not None:
        _send([proposer.email], f"Word {verdict}: {label}", Email(
            theme=theme,
            badge="Word approved" if approved else "Word not approved",
            title=f"“{english}” is now in the vocabulary" if approved else f"“{english}” wasn't approved",
            title_ta="உங்கள் சொல் சொல்லகராதியில் சேர்க்கப்பட்டது" if approved else "உங்கள் சொல் ஏற்கப்படவில்லை",
            preheader=f"{reviewer} {verdict} the word you proposed.",
            greeting=f"Hi {proposer.name},",
            intro=[f"{reviewer} {verdict} the word you proposed:"],
            rows=rows,
            note=note_block,
            outro=["Everyone can now see and record it. Its approved recordings are used the next time the model is trained."]
            if approved else ["Its recordings that were still waiting for review were rejected too."],
            action=("Open Teach Signs", _link("/teach")),
            footer=TRAINER_FOOTER,
        ))
    proposed_by = f", proposed by {proposer.name} ({proposer.email})" if proposer else ""
    _send(admins, f"Word {verdict}: {label}", Email(
        theme=theme,
        badge="Word approved" if approved else "Word rejected",
        title=f"Word {verdict}: {english}",
        title_ta="சொல் ஏற்கப்பட்டது" if approved else "சொல் நிராகரிக்கப்பட்டது",
        preheader=f"{reviewer} {verdict} “{english}”.",
        intro=[f"{reviewer} {verdict} this word{proposed_by}:"],
        rows=rows,
        note=note_block,
        action=("Open Review & Train", _link("/review")),
        footer=ADMIN_FOOTER,
    ))
