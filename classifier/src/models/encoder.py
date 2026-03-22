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
    label_mapping_path: Path | None = None
    thresholds_path: Path | None = None
    manifest_path: Path | None = None


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


def train_stronger_encoder_pipeline(texts: list[str], labels: list[str], random_state: int = 42) -> Pipeline:
    """
    Stronger CPU-friendly encoder candidate for Stage A.
    Uses word+char feature union with balanced logistic regression.
    """
    from sklearn.pipeline import FeatureUnion

    word_tfidf = TfidfVectorizer(analyzer="word", ngram_range=(1, 3), min_df=1, max_df=0.95, sublinear_tf=True)
    char_tfidf = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 6), min_df=1, max_df=0.98)
    features = FeatureUnion(
        [
            ("word_tfidf", word_tfidf),
            ("char_tfidf", char_tfidf),
        ]
    )
    return Pipeline(
        [
            ("tokenizer", features),
            (
                "classifier",
                LogisticRegression(max_iter=2500, random_state=random_state, class_weight="balanced", C=1.2),
            ),
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


def save_inference_artifact_bundle(
    model: Pipeline,
    output_dir: str | Path,
    labels: list[str],
    profile_thresholds: dict[str, dict[str, float]],
    metadata: dict,
    schema_version: str = "v2",
) -> EncoderArtifacts:
    base = Path(output_dir)
    base.mkdir(parents=True, exist_ok=True)

    model_path = base / "encoder_model.joblib"
    tokenizer_path = base / "tokenizer.joblib"
    metadata_path = base / "training_metadata.json"
    label_mapping_path = base / "label_mapping.json"
    thresholds_path = base / "thresholds.json"
    manifest_path = base / "artifact_manifest.json"

    joblib.dump(model, model_path)
    joblib.dump(model.named_steps["tokenizer"], tokenizer_path)

    label_mapping = {"labels": labels, "label_to_id": {label: idx for idx, label in enumerate(labels)}}
    label_mapping_path.write_text(json.dumps(label_mapping, ensure_ascii=False, indent=2), encoding="utf-8")
    thresholds_path.write_text(json.dumps(profile_thresholds, ensure_ascii=False, indent=2), encoding="utf-8")
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    manifest = {
        "schema_version": schema_version,
        "files": {
            "model": model_path.name,
            "tokenizer": tokenizer_path.name,
            "metadata": metadata_path.name,
            "label_mapping": label_mapping_path.name,
            "thresholds": thresholds_path.name,
        },
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    return EncoderArtifacts(
        model_path=model_path,
        tokenizer_path=tokenizer_path,
        metadata_path=metadata_path,
        label_mapping_path=label_mapping_path,
        thresholds_path=thresholds_path,
        manifest_path=manifest_path,
    )


def load_encoder_model(path: str | Path) -> Pipeline:
    return joblib.load(path)

