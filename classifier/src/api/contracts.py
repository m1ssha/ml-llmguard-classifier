from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass
class PredictionResult:
    is_malicious: bool
    binary_label: str
    binary_confidence: float
    threat_type: str | None
    threat_confidence: float | None
    signals: dict
    schema_version: str = "v2"
    deployment_profile: str = "balanced"
    thresholds: dict | None = None
    evidence: dict | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def validate_result_contract(payload: dict) -> None:
    required = {
        "is_malicious": bool,
        "binary_label": str,
        "binary_confidence": (int, float),
        "threat_type": (str, type(None)),
        "threat_confidence": (int, float, type(None)),
        "signals": dict,
    }
    optional = {
        "schema_version": str,
        "deployment_profile": str,
        "thresholds": (dict, type(None)),
        "evidence": (dict, type(None)),
    }
    for key, expected in required.items():
        if key not in payload:
            raise ValueError(f"Missing required field: {key}")
        if not isinstance(payload[key], expected):
            raise TypeError(f"Invalid type for {key}: expected {expected}, got {type(payload[key])}")

    for key, expected in optional.items():
        if key in payload and not isinstance(payload[key], expected):
            raise TypeError(f"Invalid type for {key}: expected {expected}, got {type(payload[key])}")

