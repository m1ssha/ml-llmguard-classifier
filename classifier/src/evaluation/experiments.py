from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from classifier.src.inference.rules import detect_rule_signals
from classifier.src.training.pipelines import train_baseline_pipeline, train_encoder_training_pipeline
from classifier.src.training.reproducibility import ReproConfig


@dataclass
class ExperimentSummary:
    baseline_vs_encoder: dict
    binary_vs_two_stage: dict
    rule_ablation: dict


def run_full_experiment_suite(samples: list[dict], output_path: str = "classifier/reports/experiment_summary.json") -> dict:
    baseline = train_baseline_pipeline(samples, ReproConfig(experiment_name="baseline_vs_encoder_baseline"))
    encoder = train_encoder_training_pipeline(samples, ReproConfig(experiment_name="baseline_vs_encoder_encoder"))

    binary_only = {"mode": "binary_only", "notes": "Threat stage disabled"}
    two_stage = {"mode": "two_stage", "notes": "Threat stage enabled"}

    with_rules = sum(sum(detect_rule_signals(s["text"]).as_dict().values()) > 0 for s in samples)
    without_rules = 0
    ablation = {
        "with_rules_triggered": int(with_rules),
        "without_rules_triggered": int(without_rules),
    }

    summary = ExperimentSummary(
        baseline_vs_encoder={"baseline": baseline, "encoder": encoder},
        binary_vs_two_stage={"binary_only": binary_only, "two_stage": two_stage},
        rule_ablation=ablation,
    )
    payload = {
        "baseline_vs_encoder": summary.baseline_vs_encoder,
        "binary_vs_two_stage": summary.binary_vs_two_stage,
        "rule_ablation": summary.rule_ablation,
    }

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload

