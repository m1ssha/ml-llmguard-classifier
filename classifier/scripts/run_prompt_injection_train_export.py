from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import json

import pandas as pd

from classifier.src.common.preprocessing import preprocess_batch
from classifier.src.dataset.loader import (
    HF_DATASET_ALIAS,
    LABEL_COLUMN_ALIASES,
    TEXT_COLUMN_ALIASES,
    load_hf_prompt_injection_dataset,
)
from classifier.src.dataset.validator import infer_holdout_slice
from classifier.src.evaluation.metrics import compute_binary_metrics
from classifier.src.models.baseline import save_baseline_model, train_tfidf_logreg
from classifier.src.models.encoder import save_inference_artifact_bundle, train_stronger_encoder_pipeline
from classifier.src.training.reproducibility import ReproConfig, create_experiment_dir, set_seed


PROFILE_THRESHOLDS: dict[str, dict[str, float]] = {
    "balanced": {"binary_threshold": 0.5, "threat_threshold": 0.5},
    "high_recall_security": {"binary_threshold": 0.35, "threat_threshold": 0.4},
}


@dataclass(frozen=True)
class TrainExportConfig:
    dataset_id: str = HF_DATASET_ALIAS
    output_root: str = "classifier/artifacts"
    seed: int = 42
    experiment_name: str = "prompt_injection_train_export"
    include_baseline: bool = False
    profile: str = "balanced"


def _parse_bool(value: str) -> bool:
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}. Use true/false.")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run prompt injection end-to-end training and export")
    parser.add_argument("--dataset-id", dest="dataset_id", default=HF_DATASET_ALIAS)
    parser.add_argument("--output-root", dest="output_root", default="classifier/artifacts")
    parser.add_argument("--seed", dest="seed", type=int, default=42)
    parser.add_argument("--experiment-name", dest="experiment_name", default="prompt_injection_train_export")
    parser.add_argument("--include-baseline", dest="include_baseline", type=_parse_bool, default=False)
    parser.add_argument(
        "--profile",
        dest="profile",
        choices=tuple(PROFILE_THRESHOLDS.keys()),
        default="balanced",
    )
    return parser


def _resolve_column(df: pd.DataFrame, aliases: tuple[str, ...], semantic_name: str) -> str:
    for name in aliases:
        if name in df.columns:
            return name
    raise ValueError(
        f"Missing required semantic field '{semantic_name}'. "
        f"Expected one of aliases: {list(aliases)}. "
        f"Available columns: {list(df.columns)}"
    )


def _to_binary_label(value: object) -> str:
    if isinstance(value, bool):
        return "malicious" if value else "benign"
    if isinstance(value, (int, float)):
        return "malicious" if int(value) == 1 else "benign"

    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "malicious", "attack", "prompt_injection", "yes"}:
        return "malicious"
    if normalized in {"0", "false", "benign", "no"}:
        return "benign"
    raise ValueError(f"Unsupported binary label value: {value}")


def _infer_language(text: str) -> str:
    has_cyr = any("а" <= ch.lower() <= "я" for ch in text)
    has_lat = any("a" <= ch.lower() <= "z" for ch in text)
    if has_cyr and has_lat:
        return "mixed"
    if has_cyr:
        return "ru"
    return "en"


def _normalize_split_frame(df: pd.DataFrame, split: str) -> pd.DataFrame:
    text_col = _resolve_column(df, TEXT_COLUMN_ALIASES, semantic_name="text")
    label_col = _resolve_column(df, LABEL_COLUMN_ALIASES, semantic_name="binary_label")

    result = df.copy()
    result["text"] = result[text_col].astype(str)
    result["binary_label"] = result[label_col].map(_to_binary_label)

    if "id" not in result.columns:
        result["id"] = [f"{split}_{idx}" for idx in range(len(result))]
    if "language" not in result.columns:
        result["language"] = result["text"].map(_infer_language)
    if "source" not in result.columns:
        result["source"] = f"hf:{split}"
    if "category" not in result.columns:
        result["category"] = result["binary_label"].map(lambda x: "staged" if x == "malicious" else "benign")

    result["threat_type"] = result["binary_label"].map(lambda x: "prompt_injection" if x == "malicious" else "none")
    result["prompt"] = result["text"]
    if "robustness_slice" not in result.columns:
        result["robustness_slice"] = [
            infer_holdout_slice(text, binary, language)
            for text, binary, language in zip(
                result["text"].tolist(), result["binary_label"].tolist(), result["language"].astype(str).tolist(), strict=True
            )
        ]
    return result


def _as_samples(df: pd.DataFrame) -> list[dict]:
    fields = [
        "id",
        "text",
        "prompt",
        "binary_label",
        "threat_type",
        "language",
        "source",
        "category",
        "robustness_slice",
    ]
    return df[fields].to_dict(orient="records")


def _compute_profile_metrics(y_true: list[str], y_score: list[float], threshold: float) -> dict:
    y_pred = ["malicious" if score >= threshold else "benign" for score in y_score]
    return compute_binary_metrics(y_true, y_pred, y_score)


def _compute_robustness_slices(samples: list[dict], y_score: list[float]) -> dict:
    slices: dict[str, dict[str, float | int]] = {
        "obfuscation": {"count": 0, "mean_score": 0.0},
        "policy_bypass": {"count": 0, "mean_score": 0.0},
        "multilingual_transfer": {"count": 0, "mean_score": 0.0},
        "benign_security_discussion": {"count": 0, "mean_score": 0.0},
    }
    score_sums: dict[str, float] = {name: 0.0 for name in slices}

    for sample, score in zip(samples, y_score, strict=True):
        slice_name = sample.get("robustness_slice")
        if not slice_name:
            slice_name = infer_holdout_slice(
                str(sample.get("text", "")),
                str(sample.get("binary_label", "")),
                str(sample.get("language", "")),
            )
        if slice_name not in slices:
            continue
        slices[str(slice_name)]["count"] += 1
        score_sums[str(slice_name)] += float(score)

    for name, payload in slices.items():
        count = int(payload["count"])
        payload["mean_score"] = float(score_sums[name] / count) if count else 0.0
    return slices


def run_train_export(config: TrainExportConfig) -> dict:
    if config.profile not in PROFILE_THRESHOLDS:
        raise ValueError(
            f"Unknown profile '{config.profile}'. Available profiles: {list(PROFILE_THRESHOLDS.keys())}"
        )

    set_seed(config.seed)
    experiment_dir = create_experiment_dir(
        ReproConfig(seed=config.seed, experiment_name=config.experiment_name, output_root=config.output_root)
    )

    datasets = load_hf_prompt_injection_dataset(dataset_id=config.dataset_id)
    train_df = _normalize_split_frame(datasets["train"], split="train")
    validation_df = _normalize_split_frame(datasets["validation"], split="validation")
    test_df = _normalize_split_frame(datasets["test"], split="test")

    full_train_df = pd.concat([train_df, validation_df], ignore_index=True)

    train_texts = preprocess_batch(full_train_df["text"].tolist())
    train_binary_labels = full_train_df["binary_label"].tolist()
    train_threat_labels = full_train_df["threat_type"].tolist()

    test_texts = preprocess_batch(test_df["text"].tolist())
    y_test_binary = test_df["binary_label"].tolist()

    encoder_model = train_stronger_encoder_pipeline(train_texts, train_threat_labels, random_state=config.seed)

    threat_classes = list(encoder_model.classes_)
    positive_label = "prompt_injection" if "prompt_injection" in threat_classes else threat_classes[0]
    positive_idx = threat_classes.index(positive_label)
    y_score = [float(row[positive_idx]) for row in encoder_model.predict_proba(test_texts)]

    profiles_payload = {}
    for profile_name, threshold_cfg in PROFILE_THRESHOLDS.items():
        threshold = float(threshold_cfg["binary_threshold"])
        profiles_payload[profile_name] = {
            "thresholds": threshold_cfg,
            "binary_metrics": _compute_profile_metrics(y_test_binary, y_score, threshold=threshold),
        }

    training_metadata = {
        "dataset_id": config.dataset_id,
        "seed": config.seed,
        "experiment_name": config.experiment_name,
        "output_root": config.output_root,
        "active_profile": config.profile,
        "rows": {
            "train": int(len(train_df)),
            "validation": int(len(validation_df)),
            "test": int(len(test_df)),
        },
        "train_samples": int(len(train_texts)),
        "test_samples": int(len(test_texts)),
        "model_type": "stronger_encoder_pipeline",
    }

    artifacts = save_inference_artifact_bundle(
        model=encoder_model,
        output_dir=experiment_dir,
        labels=sorted(set(train_threat_labels)),
        profile_thresholds=PROFILE_THRESHOLDS,
        metadata=training_metadata,
    )

    test_samples = _as_samples(test_df)
    robustness_slices = _compute_robustness_slices(test_samples, y_score)

    baseline_payload: dict | None = None
    if config.include_baseline:
        baseline_model = train_tfidf_logreg(train_texts, train_binary_labels, random_state=config.seed)
        baseline_path = save_baseline_model(baseline_model, experiment_dir / "baseline_model.joblib")
        baseline_scores_raw = baseline_model.predict_proba(test_texts)
        baseline_classes = list(baseline_model.classes_)
        baseline_idx = baseline_classes.index("malicious") if "malicious" in baseline_classes else 0
        baseline_scores = [float(row[baseline_idx]) for row in baseline_scores_raw]
        baseline_payload = {
            "model_path": str(baseline_path),
            "binary_metrics": {
                "balanced": _compute_profile_metrics(y_test_binary, baseline_scores, threshold=0.5),
                "high_recall_security": _compute_profile_metrics(y_test_binary, baseline_scores, threshold=0.35),
            },
        }

    evaluation_report = {
        "dataset_id": config.dataset_id,
        "profile_requested": config.profile,
        "profiles": profiles_payload,
        "robustness_slices": robustness_slices,
        "artifacts": {
            "encoder_model": str(artifacts.model_path),
            "tokenizer": str(artifacts.tokenizer_path),
            "label_mapping": str(artifacts.label_mapping_path),
            "thresholds": str(artifacts.thresholds_path),
            "training_metadata": str(artifacts.metadata_path),
            "artifact_manifest": str(artifacts.manifest_path),
        },
        "rows": {
            "train": int(len(train_df)),
            "validation": int(len(validation_df)),
            "test": int(len(test_df)),
        },
    }
    if baseline_payload is not None:
        evaluation_report["baseline"] = baseline_payload

    evaluation_report_path = Path(experiment_dir) / "evaluation_report.json"
    evaluation_report_path.write_text(json.dumps(evaluation_report, ensure_ascii=False, indent=2), encoding="utf-8")

    manifest_path = Path(artifacts.manifest_path)
    manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    files_payload = dict(manifest_payload.get("files", {}))
    files_payload["evaluation_report"] = evaluation_report_path.name
    if baseline_payload is not None:
        files_payload["baseline_model"] = "baseline_model.joblib"
    manifest_payload["files"] = files_payload
    manifest_payload["profile_requested"] = config.profile
    manifest_payload["dataset_id"] = config.dataset_id
    manifest_path.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    result = {
        "experiment_dir": str(experiment_dir),
        "evaluation_report": str(evaluation_report_path),
        "manifest": str(manifest_path),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main() -> None:
    args = _build_parser().parse_args()
    config = TrainExportConfig(
        dataset_id=args.dataset_id,
        output_root=args.output_root,
        seed=args.seed,
        experiment_name=args.experiment_name,
        include_baseline=args.include_baseline,
        profile=args.profile,
    )
    run_train_export(config)


if __name__ == "__main__":
    main()
