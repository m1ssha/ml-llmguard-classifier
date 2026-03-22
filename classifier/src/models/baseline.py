from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


@dataclass
class BaselineArtifacts:
    model_path: Path
    metrics_path: Path


def train_tfidf_logreg(texts: list[str], labels: list[str], random_state: int = 42) -> Pipeline:
    return Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_df=0.95)),
            ("logreg", LogisticRegression(max_iter=1500, random_state=random_state)),
        ]
    ).fit(texts, labels)


def save_baseline_model(model: Pipeline, output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output)
    return output


def load_baseline_model(path: str | Path) -> Pipeline:
    return joblib.load(path)

