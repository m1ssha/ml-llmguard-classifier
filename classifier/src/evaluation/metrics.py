from __future__ import annotations

from dataclasses import dataclass

from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
    precision_score,
    recall_score,
    roc_auc_score,
)


MANDATORY_BINARY = ("accuracy", "precision", "recall", "f1", "roc_auc")
MANDATORY_MULTICLASS = ("macro_f1", "weighted_f1", "confusion_matrix", "per_class")


@dataclass
class MetricsBundle:
    binary: dict
    multiclass: dict


def compute_binary_metrics(y_true: list[str], y_pred: list[str], y_score: list[float]) -> dict:
    y_true_bin = [1 if y == "malicious" else 0 for y in y_true]
    y_pred_bin = [1 if y == "malicious" else 0 for y in y_pred]
    return {
        "accuracy": accuracy_score(y_true_bin, y_pred_bin),
        "precision": precision_score(y_true_bin, y_pred_bin, zero_division=0),
        "recall": recall_score(y_true_bin, y_pred_bin, zero_division=0),
        "f1": f1_score(y_true_bin, y_pred_bin, zero_division=0),
        "roc_auc": roc_auc_score(y_true_bin, y_score) if len(set(y_true_bin)) > 1 else 0.5,
    }


def compute_multiclass_metrics(y_true: list[str], y_pred: list[str], labels: list[str]) -> dict:
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=labels,
        zero_division=0,
    )
    return {
        "macro_f1": f1_score(y_true, y_pred, average="macro", zero_division=0),
        "weighted_f1": f1_score(y_true, y_pred, average="weighted", zero_division=0),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=labels).tolist(),
        "per_class": {
            label: {"precision": float(precision[i]), "recall": float(recall[i]), "f1": float(f1[i])}
            for i, label in enumerate(labels)
        },
    }


def validate_metrics_completeness(bundle: MetricsBundle) -> None:
    missing_binary = [m for m in MANDATORY_BINARY if m not in bundle.binary]
    missing_multi = [m for m in MANDATORY_MULTICLASS if m not in bundle.multiclass]
    if missing_binary or missing_multi:
        raise ValueError(f"Metrics report incomplete: binary={missing_binary}, multiclass={missing_multi}")

