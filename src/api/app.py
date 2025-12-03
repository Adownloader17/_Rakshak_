# src/api/app.py
from pathlib import Path
import os
import logging
from typing import List, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from joblib import load

import pandas as pd

from src.features.url_features import extract_basic_features
from src.features.xss_features import extract_xss_features

# ---------------------------------------
# App + Logging
# ---------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rakshak.api")

app = FastAPI(title="Rakshak API", version="0.1")

# Allow local dev origins (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://localhost:8000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------
# Models directory and lazy loaders
# ---------------------------------------
ROOT_DIR = Path(__file__).resolve().parents[1]  # src/
MODEL_DIR = ROOT_DIR / "models"

_phishing_model = None
_xss_model = None

def _model_path(name: str) -> Path:
    return MODEL_DIR / name

def get_phishing_model():
    global _phishing_model
    if _phishing_model is None:
        path = _model_path("phishing_model.joblib")
        if not path.exists():
            raise RuntimeError(f"phishing_model not found at {path}. Train the model first.")
        logger.info(f"Loading phishing model from {path}")
        _phishing_model = load(path)
    return _phishing_model

def get_xss_model():
    global _xss_model
    if _xss_model is None:
        path = _model_path("xss_model.joblib")
        if not path.exists():
            raise RuntimeError(f"xss_model not found at {path}. Train the model first.")
        logger.info(f"Loading xss model from {path}")
        _xss_model = load(path)
    return _xss_model

# ---------------------------------------
# Helpers
# ---------------------------------------
def score_from_model(model: Any, X: pd.DataFrame) -> float:
    """
    Return a probability-like score in [0,1] for the first row of X.
    This tries predict_proba, then predict, then model.predict (LightGBM).
    """
    # try sklearn predict_proba
    try:
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(X)
            # proba could be shape (n,2) or (n,1)
            if proba.ndim == 2 and proba.shape[1] > 1:
                return float(proba[0, 1])
            else:
                # single-column probability or other shape
                return float(proba[0].item())
    except Exception:
        logger.debug("predict_proba failed, trying predict()", exc_info=True)

    # try sklearn-like predict
    try:
        preds = model.predict(X)
        # preds may be probabilities (floats) or class labels (0/1)
        if hasattr(preds, "__len__"):
            first = preds[0]
            if isinstance(first, float):
                # already a probability-like float
                # bounds check
                if 0.0 <= first <= 1.0:
                    return float(first)
                # otherwise, maybe raw score; apply logistic sigmoid
                import math
                return 1.0 / (1.0 + math.exp(-float(first)))
            else:
                # assume label-like: map 1->1.0, else 0.0
                return 1.0 if int(first) != 0 else 0.0
        else:
            # scalar single prediction
            val = float(preds)
            if 0.0 <= val <= 1.0:
                return val
            import math
            return 1.0 / (1.0 + math.exp(-val))
    except Exception:
        logger.debug("predict failed", exc_info=True)

    # as a last resort, raise
    raise RuntimeError("Model did not return a usable score via predict_proba or predict.")

# ---------------------------------------
# Request models
# ---------------------------------------
class URLPayload(BaseModel):
    url: str

class XSSPayload(BaseModel):
    payload: str

# ---------------------------------------
# Routes
# ---------------------------------------
@app.get("/")
def root():
    return {"message": "Rakshak API Running Successfully 🚀", "models_dir": str(MODEL_DIR)}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict/url")
def predict_url(payload: URLPayload):
    try:
        df = pd.DataFrame([{"url": payload.url}])
        df = extract_basic_features(df)
        feature_cols = ['len','has_ip','digits','subdirs','dashes','has_at']
        X = df[feature_cols]
        model = get_phishing_model()
        score = score_from_model(model, X)
        label = "phishing" if score > 0.5 else "benign"
        reasons: List[str] = []
        if int(df.loc[0, 'has_ip']) == 1:
            reasons.append("contains IP")
        if int(df.loc[0, 'has_at']) == 1:
            reasons.append("contains @")
        if int(df.loc[0, 'digits']) > 10:
            reasons.append("many digits")
        return {"label": label, "score": float(score), "reasons": reasons}
    except Exception as e:
        logger.exception("Error in /predict/url")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/xss")
def predict_xss(payload: XSSPayload):
    try:
        df = pd.DataFrame([{"payload": payload.payload}])
        df = extract_xss_features(df)
        feature_cols = ['len','num_script','num_iframe','num_on_events','num_js_proto',
                        'num_eval','num_alert','num_tags','num_quotes','tags_ratio']
        X = df[feature_cols]
        model = get_xss_model()
        score = score_from_model(model, X)
        label = "malicious" if score > 0.5 else "clean"
        reasons: List[str] = []
        if int(df.loc[0, 'num_script']) > 0:
            reasons.append("script tag")
        if int(df.loc[0, 'num_on_events']) > 0:
            reasons.append("on* event handler")
        if int(df.loc[0, 'num_js_proto']) > 0:
            reasons.append("javascript: proto")
        return {"label": label, "score": float(score), "reasons": reasons}
    except Exception as e:
        logger.exception("Error in /predict/xss")
        raise HTTPException(status_code=500, detail=str(e))
