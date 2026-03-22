from __future__ import annotations

from pathlib import Path
import json

from classifier.src.common.preprocessing import preprocess_batch
from classifier.src.dataset.loader import load_hf_prompt_injection_dataset
from classifier.src.dataset.validator import infer_holdout_slice
from classifier.src.evaluation.metrics import compute_binary_metrics
from classifier.src.inference.rules import detect_rule_signals
from classifier.src.models.baseline import train_tfidf_logreg


def _to_binary_label(value: object) -> str:
    if isinstance(value, bool):
        return "malicious" if value else "benign"
    if isinstance(value, (int, float)):
        return "malicious" if int(value) == 1 else "benign"
    text = str(value).strip().lower()
    return "malicious" if text in {"1", "malicious", "attack", "prompt_injection", "true", "yes"} else "benign"


def _extract_labels(df) -> list[str]:
    for candidate in ("binary_label", "label", "is_malicious", "target"):
        if candidate in df.columns:
            return [_to_binary_label(v) for v in df[candidate].tolist()]
    raise ValueError("Не найдена колонка с бинарной разметкой. Ожидается одна из: binary_label, label, is_malicious, target")


def _infer_language(text: str) -> str:
    has_cyr = any("а" <= ch.lower() <= "я" for ch in text)
    has_lat = any("a" <= ch.lower() <= "z" for ch in text)
    if has_cyr and has_lat:
        return "mixed"
    if has_cyr:
        return "ru"
    return "en"


def _compute_profile_metrics(y_true: list[str], y_score: list[float], threshold: float) -> dict:
    y_pred = ["malicious" if score >= threshold else "benign" for score in y_score]
    return compute_binary_metrics(y_true, y_pred, y_score)


def main() -> None:
    datasets = load_hf_prompt_injection_dataset()

    train_df = datasets["train"]
    validation_df = datasets["validation"]
    test_df = datasets["test"]

    if "text" not in train_df.columns or "text" not in validation_df.columns or "text" not in test_df.columns:
        raise ValueError("В датасете отсутствует обязательная колонка `text`")

    train_texts = preprocess_batch(train_df["text"].astype(str).tolist() + validation_df["text"].astype(str).tolist())
    train_labels = _extract_labels(train_df) + _extract_labels(validation_df)

    test_texts_raw = test_df["text"].astype(str).tolist()
    test_texts = preprocess_batch(test_texts_raw)
    test_labels = _extract_labels(test_df)

    model = train_tfidf_logreg(train_texts, train_labels, random_state=42)
    proba = model.predict_proba(test_texts)
    malicious_idx = list(model.classes_).index("malicious") if "malicious" in model.classes_ else 0
    scores = [float(row[malicious_idx]) for row in proba]

    balanced_threshold = 0.5
    high_recall_threshold = 0.35

    balanced_metrics = _compute_profile_metrics(test_labels, scores, threshold=balanced_threshold)
    high_recall_metrics = _compute_profile_metrics(test_labels, scores, threshold=high_recall_threshold)

    holdout_counts = {
        "obfuscation": 0,
        "policy_bypass": 0,
        "multilingual_transfer": 0,
        "benign_security_discussion": 0,
    }
    false_positive_proxy = {k: 0 for k in holdout_counts}

    for raw_text, score, y_true in zip(test_texts_raw, scores, test_labels, strict=True):
        language = _infer_language(raw_text)
        slice_name = infer_holdout_slice(raw_text, y_true, language)
        if not slice_name:
            continue
        holdout_counts[slice_name] += 1

        rule_triggered = sum(detect_rule_signals(raw_text).as_dict().values()) > 0
        is_false_positive_proxy = y_true == "benign" and score >= balanced_threshold
        if rule_triggered or is_false_positive_proxy:
            false_positive_proxy[slice_name] += 1

    payload = {
        "dataset": "neuralchemy/Prompt-injection-dataset",
        "rows": {
            "train": int(len(train_df)),
            "validation": int(len(validation_df)),
            "test": int(len(test_df)),
        },
        "profiles": {
            "balanced": {"threshold": balanced_threshold, "metrics": balanced_metrics},
            "high_recall_security": {"threshold": high_recall_threshold, "metrics": high_recall_metrics},
        },
        "robustness": {
            "holdout_counts": holdout_counts,
            "false_positive_proxy": false_positive_proxy,
        },
    }

    output_path = Path("classifier/reports/prompt_injection_eval_metrics.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"Saved metrics to: {output_path}")


if __name__ == "__main__":
    main()
