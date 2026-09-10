from fastapi import APIRouter

router = APIRouter()


@router.post("/speech-to-text")
def speech_to_text():
    """STUB for the hackathon MVP. Real speech-to-text (for the hearing
    person's side of the conversation, MODE B in the spec) should use the
    browser's built-in Web Speech API client-side first - it's free, needs
    no backend call, and keeps audio local. Only wire this endpoint to a
    server-side ASR provider if the browser API proves insufficient, and
    document whatever provider/license you choose in DATA_LICENSE.md."""
    return {
        "implemented": False,
        "note": "Use the browser's Web Speech API client-side for the MVP demo.",
    }
