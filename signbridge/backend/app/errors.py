from fastapi import HTTPException


class ApiError(HTTPException):
    """An error the app explains itself: `code` lets the UI word it in Tamil or
    English, `message` is readable English, and extra fields carry details."""

    def __init__(self, status_code: int, code: str, message: str, **extra):
        super().__init__(status_code=status_code, detail={"code": code, "message": message, **extra})
