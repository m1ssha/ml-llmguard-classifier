from __future__ import annotations

from pathlib import Path
import json

from classifier.src.common.preprocessing import preprocess_batch
from classifier.src.dataset.loader import load_hf_prompt_injection_dataset
from classifier.src.evaluation.metrics import compute_binary_metrics
from classifier.src.models.baseline import train_tfidf_logreg


def _to_binary_label(value: object) -> str:
    if isinstance(value, bool):
        return "malicious" if value else "benign"
    if isinstance(value, (int, float)):
        return "malicious" if int(value) == 1 else "benign"
    text = str(value).strip().lower()
    return "malicious" if text in {"1", "malicious", "attack", "prompt_injection", "true"} else "benign"


def _extract_labels(df) -> list[str]:
    for candidate in ("binary_label", "label", "is_malicious", "target"):
        if candidate in df.columns:
            return [_to_binary_label(v) for v in df[candidate].tolist()]
    raise ValueError("Не найдена колонка с бинарной разметкой. Ожидается одна из: binary_label, label, is_malicious, target")


def main() -> None:
    datasets = load_hf_prompt_injection_dataset()

    train_df = datasets["train"]
    validation_df = datasets["validation"]
    test_df = datasets["test"]

    if "text" not in train_df.columns or "text" not in test_df.columns:
        raise ValueError("В датасете отсутствует обязательная колонка `text`")

    train_texts = preprocess_batch(train_df["text"].astype(str).tolist() + validation_df["text"].astype(str).tolist())
    train_labels = _extract_labels(train_df) + _extract_labels(validation_df)
    test_texts = preprocess_batch(test_df["text"].astype(str).tolist())
    test_labels = _extract_labels(test_df)

    model = train_tfidf_logreg(train_texts, train_labels, random_state=42)
    pred = model.predict(test_texts).tolist()
    proba = model.predict_proba(test_texts)
    malicious_idx = list(model.classes_).index("malicious") if "malicious" in model.classes_ else 0
    scores = [float(row[malicious_idx]) for row in proba]

    metrics = compute_binary_metrics(test_labels, pred, scores)

    output_path = Path("classifier/reports/hf_eval_metrics.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    print(f"Saved metrics to: {output_path}")


if __name__ == "__main__":
    main()

