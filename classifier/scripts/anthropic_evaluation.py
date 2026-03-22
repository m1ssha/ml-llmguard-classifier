from __future__ import annotations

import argparse
from pathlib import Path
import json

from classifier.src.common.preprocessing import preprocess_batch
from classifier.src.dataset.loader import HFDatasetSource, load_source_split
from classifier.src.evaluation.metrics import compute_binary_metrics
from classifier.src.models.baseline import train_tfidf_logreg


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate baseline model on Anthropic/hh-rlhf with policy A")
    parser.add_argument("--dataset-id", dest="dataset_id", default="Anthropic/hh-rlhf")
    parser.add_argument("--train-split", dest="train_split", default="train")
    parser.add_argument("--validation-split", dest="validation_split", default="test")
    parser.add_argument("--test-split", dest="test_split", default="test")
    parser.add_argument("--revision", dest="revision", default=None)
    parser.add_argument("--seed", dest="seed", type=int, default=42)
    parser.add_argument(
        "--output",
        dest="output",
        default="classifier/reports/anthropic_eval_metrics.json",
        help="Path to output metrics JSON",
    )
    return parser


def _build_source(dataset_id: str, train_split: str, validation_split: str, test_split: str, revision: str | None) -> HFDatasetSource:
    return HFDatasetSource(
        name="hh_rlhf",
        dataset_id=dataset_id,
        split_map={"train": train_split, "validation": validation_split, "test": test_split},
        revision=revision,
        mapping_policy="chosen_rejected_policy_a",
        role="alignment_aux",
    )


def _collect_rows(source: HFDatasetSource) -> tuple[dict[str, int], list[str], list[str], list[str], list[str], list[str]]:
    train_df = load_source_split(source, "train")
    validation_df = load_source_split(source, "validation")
    test_df = load_source_split(source, "test")

    train_texts = preprocess_batch(train_df["text"].astype(str).tolist() + validation_df["text"].astype(str).tolist())
    train_labels = train_df["binary_label"].astype(str).tolist() + validation_df["binary_label"].astype(str).tolist()

    test_texts = preprocess_batch(test_df["text"].astype(str).tolist())
    test_labels = test_df["binary_label"].astype(str).tolist()
    test_origins = test_df["origin_field"].astype(str).tolist() if "origin_field" in test_df.columns else ["unknown"] * len(test_df)

    rows = {
        "train": int(len(train_df)),
        "validation": int(len(validation_df)),
        "test": int(len(test_df)),
    }
    return rows, train_texts, train_labels, test_texts, test_labels, test_origins


def _origin_breakdown(y_true: list[str], y_score: list[float], origins: list[str], threshold: float) -> dict[str, dict[str, float | int]]:
    payload: dict[str, dict[str, float | int]] = {}
    for origin in sorted(set(origins)):
        indices = [i for i, candidate in enumerate(origins) if candidate == origin]
        if not indices:
            continue
        origin_true = [y_true[i] for i in indices]
        origin_score = [y_score[i] for i in indices]
        origin_pred = ["malicious" if score >= threshold else "benign" for score in origin_score]
        fp = sum(1 for truth, pred in zip(origin_true, origin_pred, strict=True) if truth == "benign" and pred == "malicious")
        fn = sum(1 for truth, pred in zip(origin_true, origin_pred, strict=True) if truth == "malicious" and pred == "benign")
        payload[origin] = {
            "count": len(indices),
            "false_positive": fp,
            "false_negative": fn,
        }
    return payload


def main() -> None:
    args = _build_parser().parse_args()
    source = _build_source(
        dataset_id=args.dataset_id,
        train_split=args.train_split,
        validation_split=args.validation_split,
        test_split=args.test_split,
        revision=args.revision,
    )

    rows, train_texts, train_labels, test_texts, test_labels, test_origins = _collect_rows(source)

    model = train_tfidf_logreg(train_texts, train_labels, random_state=args.seed)
    prediction = model.predict(test_texts).tolist()
    proba = model.predict_proba(test_texts)
    malicious_idx = list(model.classes_).index("malicious") if "malicious" in model.classes_ else 0
    scores = [float(row[malicious_idx]) for row in proba]

    balanced_threshold = 0.5
    high_recall_threshold = 0.35

    balanced_metrics = compute_binary_metrics(
        test_labels,
        ["malicious" if score >= balanced_threshold else "benign" for score in scores],
        scores,
    )
    high_recall_metrics = compute_binary_metrics(
        test_labels,
        ["malicious" if score >= high_recall_threshold else "benign" for score in scores],
        scores,
    )

    payload = {
        "dataset": args.dataset_id,
        "mapping_policy": "chosen_rejected_policy_a",
        "revision": args.revision or "latest",
        "rows": rows,
        "profiles": {
            "balanced": {
                "threshold": balanced_threshold,
                "metrics": balanced_metrics,
                "origin_breakdown": _origin_breakdown(test_labels, scores, test_origins, balanced_threshold),
            },
            "high_recall_security": {
                "threshold": high_recall_threshold,
                "metrics": high_recall_metrics,
                "origin_breakdown": _origin_breakdown(test_labels, scores, test_origins, high_recall_threshold),
            },
        },
        "artifacts": {
            "script": "classifier/scripts/anthropic_evaluation.py",
        },
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"Saved metrics to: {output_path}")


if __name__ == "__main__":
    main()
