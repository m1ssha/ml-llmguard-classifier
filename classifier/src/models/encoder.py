from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


@dataclass
class EncoderArtifacts:
    model_path: Path
    tokenizer_path: Path
    metadata_path: Path


def train_encoder_pipeline(texts: list[str], labels: list[str], random_state: int = 42) -> Pipeline:
    """
    CPU-friendly encoder-like pipeline.
    В MVP использует subword-char TF-IDF + LR как лёгкий surrogate encoder.
    """
    return Pipeline(
        [
            (
                "tokenizer",
                TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1, max_df=0.95),
            ),
            ("classifier", LogisticRegression(max_iter=2000, random_state=random_state)),
        ]
    ).fit(texts, labels)


def save_encoder_artifacts(
    model: Pipeline,
    output_dir: str | Path,
    metadata: dict,
) -> EncoderArtifacts:
    base = Path(output_dir)
    base.mkdir(parents=True, exist_ok=True)

    model_path = base / "encoder_model.joblib"
    tokenizer_path = base / "tokenizer.joblib"
    metadata_path = base / "training_metadata.json"

    joblib.dump(model, model_path)
    joblib.dump(model.named_steps["tokenizer"], tokenizer_path)
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    return EncoderArtifacts(model_path=model_path, tokenizer_path=tokenizer_path, metadata_path=metadata_path)


def load_encoder_model(path: str | Path) -> Pipeline:
    return joblib.load(path)

