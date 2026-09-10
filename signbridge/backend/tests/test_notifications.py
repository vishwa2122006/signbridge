"""Every email renders as plain text and HTML, and text from users is escaped."""

from app.services import mailer, notifications
from app.services.notifications import IDLE_LABEL, Person

WATER = "Water / தண்ணீர்"
THUMBS = "Thumbs up / கட்டைவிரல் மேலே"


def test_every_email_has_text_and_escaped_html():
    mailer.outbox.clear()
    eve = Person("<b>Eve</b>", "eve@example.com")
    admins = ["admin@example.com"]
    notifications.send_code(eve.name, eve.email, "123456", "register")
    notifications.trainer_registered(eve, [("City", "<script>alert(1)</script>")], admins)
    notifications.samples_submitted(eve, [(WATER, 3), (IDLE_LABEL, 2)], admins)
    notifications.word_proposed(eve, THUMBS, admins)
    notifications.samples_reviewed(eve, "Admin", [(WATER, 2)], [(WATER, 1)], "<i>blurry</i>")
    notifications.review_summary("Admin", [(eve, 2, 1)], "blurry", admins)
    notifications.word_reviewed(eve, "Admin", THUMBS, "rejected", "Already exists", admins)

    assert len(mailer.outbox) == 11
    for message in mailer.outbox:
        html = message["html"]
        assert html.startswith("<!DOCTYPE html>") and message["text"], message["subject"]
        assert "<b>Eve</b>" not in html and "<script>" not in html and "<i>blurry</i>" not in html
    code = mailer.outbox[0]
    assert "123456" in code["text"] and "&lt;b&gt;Eve&lt;/b&gt;" in code["html"]
    reviewed = next(m for m in mailer.outbox if m["subject"].startswith("Your recordings were reviewed"))
    assert "கட்டைவிரல்" not in reviewed["html"] and "தண்ணீர்" in reviewed["html"]
    assert "Note from the admin: <i>blurry</i>" in reviewed["text"]
