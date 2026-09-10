from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.ml.classifier import SignClassifier
from app.routers import predict, samples, signs, train, translate
from app.services.recognition import engine


@asynccontextmanager
async def lifespan(_app: FastAPI):
    classifier = SignClassifier.load()
    if classifier is not None:
        engine.load_classifier(classifier)
    yield


app = FastAPI(
    title="SignBridge API",
    description="Sign language to English and Tamil text. Communication aid, not a certified interpreter.",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten before any real deployment
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router, tags=["recognition"])
app.include_router(signs.router, tags=["vocabulary"])
app.include_router(samples.router, tags=["training data"])
app.include_router(train.router, tags=["training"])
app.include_router(translate.router, tags=["sentences"])


@app.get("/")
def root():
    return {"name": "SignBridge API", "status": "ok", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": engine.model_loaded, "model": engine.model_metadata}
