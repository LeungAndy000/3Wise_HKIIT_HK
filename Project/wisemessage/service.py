"""Message-content API. No inbox access, link fetching, or message-content logs."""

from contextlib import asynccontextmanager
import os
from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, StrictStr, field_validator

from .predictor import MAX_MESSAGE_LENGTH, validate_message


class PredictRequest(BaseModel):
    messages: Annotated[list[StrictStr], Field(min_length=1, max_length=64)]

    @field_validator("messages")
    @classmethod
    def nonempty_messages(cls, messages):
        return [validate_message(message) for message in messages]


class ScanTextRequest(BaseModel):
    text: Annotated[StrictStr, Field(min_length=1, max_length=MAX_MESSAGE_LENGTH)]

    @field_validator("text")
    @classmethod
    def nonempty_text(cls, value):
        return validate_message(value)


class ClassScores(BaseModel):
    normal: Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]
    spam: Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]
    scam: Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]


class Thresholds(BaseModel):
    spam: Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]
    scam: Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]
    unwanted: Annotated[float | None, Field(ge=0, le=1, allow_inf_nan=False)] = None


class Prediction(BaseModel):
    model_id: str
    predicted_label: Literal["normal", "spam", "scam"]
    scores: ClassScores
    unwanted_score: Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]
    decision: Literal["flag_for_review", "below_threshold", "uncertain"]
    thresholds: Thresholds


class PredictResponse(BaseModel):
    results: list[Prediction]


def create_app(model_dir=None, *, predictor=None, device_target="CPU"):
    @asynccontextmanager
    async def lifespan(app):
        app.state.predictor = predictor
        app.state.startup_error = False
        if app.state.predictor is None:
            directory = model_dir or os.environ.get("WISEMESSAGE_MODEL_DIR")
            if directory:
                try:
                    from .predictor import MessagePredictor
                    app.state.predictor = MessagePredictor(directory, device_target=device_target)
                except Exception:
                    app.state.startup_error = True
            else:
                app.state.startup_error = True
        yield
        app.state.predictor = None

    app = FastAPI(title="WiseMessage Chinese SMS Screening", version="1.0.0", lifespan=lifespan)

    def active_predictor():
        instance = getattr(app.state, "predictor", None)
        if instance is None:
            raise HTTPException(status_code=503, detail="A trained message classifier is not ready")
        return instance

    def classify(messages):
        instance = active_predictor()
        try:
            predictions = instance.predict(messages)
            if len(predictions) != len(messages):
                raise RuntimeError("Unexpected prediction count")
            return [Prediction.model_validate(item).model_dump() for item in predictions]
        except Exception as exc:
            raise HTTPException(status_code=503, detail="Model inference is temporarily unavailable") from exc

    @app.get("/health")
    def health():
        instance = active_predictor()
        return {"status": "ready", "model_id": instance.model_id,
                "labels": ["normal", "spam", "scam"], "fetches_urls": False}

    @app.post("/predict", response_model=PredictResponse, response_model_exclude_none=True)
    def predict(request: PredictRequest):
        return {"results": classify(request.messages)}

    @app.post("/scan-text", response_model=Prediction, response_model_exclude_none=True)
    def scan_text(request: ScanTextRequest):
        return classify([request.text])[0]

    return app
