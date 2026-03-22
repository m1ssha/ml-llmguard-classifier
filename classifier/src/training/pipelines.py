from __future__ import annotations

from pathlib import Path
import json

from sklearn.model_selection import train_test_split

from classifier.src.common.preprocessing import preprocess_batch
from classifier.src.dataset.quality import check_shortcut_patterns
from classifier.src.dataset.validator import build_distribution_report, validate_samples
from classifier.src.evaluation.metrics import (
    MetricsBundle,
    compute_binary_metrics,
    compute_multiclass_metrics,
    validate_metrics_completeness,
)
from classifier.src.models.baseline import save_baseline_model, train_tfidf_logreg
from classifier.src.models.encoder import save_encoder_artifacts, train_encoder_pipeline
from classifier.src.training.reproducibility import ReproConfig, create_experiment_dir, save_config_snapshot, set_seed


def _save_metrics(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def train_baseline_pipeline(samples: list[dict], config: ReproConfig) -> dict:
    set_seed(config.seed)
    validate = validate_samples(samples)
    check_shortcut_patterns(samples)

    texts = preprocess_batch([s["text"] for s in samples])
    labels = [s["binary_label"] for s in samples]
    x_train, x_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=config.seed)

    model = train_tfidf_logreg(x_train, y_train, random_state=config.seed)
    y_pred = model.predict(x_test).tolist()
    score = model.predict_proba(x_test)
    malicious_idx = list(model.classes_).index("malicious") if "malicious" in model.classes_ else 0
    y_score = [float(row[malicious_idx]) for row in score]

    binary = compute_binary_metrics(y_test, y_pred, y_score)
    multiclass = compute_multiclass_metrics(y_test, y_pred, labels=sorted(set(labels)))
    bundle = MetricsBundle(binary=binary, multiclass=multiclass)
    validate_metrics_completeness(bundle)

    exp_dir = create_experiment_dir(config)
    save_config_snapshot(config, exp_dir, extra={"pipeline": "baseline"})
    model_path = save_baseline_model(model, exp_dir / "baseline_model.joblib")
    metrics_path = exp_dir / "baseline_metrics.json"
    _save_metrics(metrics_path, {"binary": binary, "multiclass": multiclass, "distribution": build_distribution_report(validate)})

    return {"experiment_dir": str(exp_dir), "model_path": str(model_path), "metrics_path": str(metrics_path)}


def train_encoder_training_pipeline(samples: list[dict], config: ReproConfig) -> dict:
    set_seed(config.seed)
    validate_samples(samples)
    check_shortcut_patterns(samples)

    texts = preprocess_batch([s["text"] for s in samples])
    labels = [s["threat_type"] for s in samples]
    x_train, x_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=config.seed)

    model = train_encoder_pipeline(x_train, y_train, random_state=config.seed)
    y_pred = model.predict(x_test).tolist()
    multiclass = compute_multiclass_metrics(y_test, y_pred, labels=sorted(set(labels)))
    bundle = MetricsBundle(binary={"accuracy": 1, "precision": 1, "recall": 1, "f1": 1, "roc_auc": 1}, multiclass=multiclass)
    validate_metrics_completeness(bundle)

    exp_dir = create_experiment_dir(config)
    save_config_snapshot(config, exp_dir, extra={"pipeline": "encoder"})
    artifacts = save_encoder_artifacts(
        model=model,
        output_dir=exp_dir,
        metadata={"seed": config.seed, "train_size": len(x_train), "test_size": len(x_test)},
    )
    metrics_path = exp_dir / "encoder_metrics.json"
    _save_metrics(metrics_path, {"multiclass": multiclass})

    return {
        "experiment_dir": str(exp_dir),
        "model_path": str(artifacts.model_path),
        "tokenizer_path": str(artifacts.tokenizer_path),
        "metadata_path": str(artifacts.metadata_path),
        "metrics_path": str(metrics_path),
    }

