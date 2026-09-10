from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import predict, signs, feedback, templates, speech

app = FastAPI(
    title="SignBridge API",
    description=(
        "Accessibility communication assistant prototype. "
        "NOT a medical diagnosis system. NOT a certified interpreter replacement. "
        "See RESPONSIBLE_AI.md."
    ),
    version="0.1.0-hackathon-prototype",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten before any real deployment
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router, tags=["recognition"])
app.include_router(signs.router, tags=["vocabulary"])
app.include_router(feedback.router, tags=["community-validation"])
app.include_router(templates.router, tags=["sentence-templates"])
app.include_router(speech.router, tags=["speech"])


@app.get("/")
def root():
    return {
        "name": "SignBridge API",
        "status": "ok",
        "disclaimer": (
            "Communication assistance only. This system does not provide "
            "medical diagnosis or medical advice. Prototype with a limited, "
            "unverified vocabulary - see DATASET_SOURCES.md."
        ),
    }


@app.get("/health")
def health():
    from app.services.recognition import engine
    return {"status": "ok", "model_loaded": engine.model_loaded}
