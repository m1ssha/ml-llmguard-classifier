from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from classifier.src.inference.rules import detect_rule_signals
from classifier.src.dataset.validator import build_adversarial_holdout_splits
from classifier.src.training.pipelines import (
    train_baseline_pipeline,
    train_encoder_training_pipeline,
    train_stronger_encoder_training_pipeline,
)
from classifier.src.training.reproducibility import ReproConfig


@dataclass
class ExperimentSummary:
    baseline_vs_encoder: dict
    surrogate_vs_stronger_encoder: dict
    binary_vs_two_stage: dict
    rule_ablation: dict
    robustness: dict
    calibration_profiles: dict


def run_full_experiment_suite(samples: list[dict], output_path: str = "classifier/reports/experiment_summary.json") -> dict:
    baseline = train_baseline_pipeline(samples, ReproConfig(experiment_name="baseline_vs_encoder_baseline"))
    surrogate_encoder = train_encoder_training_pipeline(samples, ReproConfig(experiment_name="baseline_vs_encoder_encoder"))
    stronger_encoder = train_stronger_encoder_training_pipeline(samples, ReproConfig(experiment_name="stronger_encoder_candidate"))

    binary_only = {"mode": "binary_only", "notes": "Threat stage disabled"}
    two_stage = {"mode": "two_stage", "notes": "Threat stage enabled"}

    with_rules = sum(sum(detect_rule_signals(s["text"]).as_dict().values()) > 0 for s in samples)
    without_rules = 0
    ablation = {
        "with_rules_triggered": int(with_rules),
        "without_rules_triggered": int(without_rules),
    }

    holdout_splits = build_adversarial_holdout_splits(samples)
    robustness = {slice_name: {"count": len(slice_samples)} for slice_name, slice_samples in holdout_splits.items()}

    benign_security_slice = holdout_splits.get("benign_security_discussion", [])
    benign_security_fp = sum(1 for s in benign_security_slice if sum(detect_rule_signals(s["text"]).as_dict().values()) > 0)
    robustness["benign_security_discussion"]["rule_false_positive_proxy"] = benign_security_fp

    deployment_profiles = {
        "balanced": {"binary_threshold": 0.5, "threat_threshold": 0.5},
        "high_recall_security": {"binary_threshold": 0.35, "threat_threshold": 0.4},
    }

    summary = ExperimentSummary(
        baseline_vs_encoder={"baseline": baseline, "encoder": surrogate_encoder},
        surrogate_vs_stronger_encoder={"surrogate": surrogate_encoder, "stronger": stronger_encoder},
        binary_vs_two_stage={"binary_only": binary_only, "two_stage": two_stage},
        rule_ablation=ablation,
        robustness=robustness,
        calibration_profiles=deployment_profiles,
    )
    payload = {
        "baseline_vs_encoder": summary.baseline_vs_encoder,
        "surrogate_vs_stronger_encoder": summary.surrogate_vs_stronger_encoder,
        "binary_vs_two_stage": summary.binary_vs_two_stage,
        "rule_ablation": summary.rule_ablation,
        "robustness": summary.robustness,
        "calibration_profiles": summary.calibration_profiles,
    }

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload

