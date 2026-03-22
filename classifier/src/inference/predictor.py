from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json

from classifier.src.api.contracts import PredictionResult, validate_result_contract
from classifier.src.common.preprocessing import normalize_text
from classifier.src.inference.rules import detect_rule_signals


@dataclass
class InferenceModels:
    binary_model: object
    threat_model: object


class TwoStagePredictor:
    def __init__(self, models: InferenceModels, audit_log_path: str = "classifier/reports/audit_log.jsonl") -> None:
        self.models = models
        self.audit_log_path = Path(audit_log_path)
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)

    def predict(self, text: str) -> dict:
        normalized = normalize_text(text)
        signals = detect_rule_signals(normalized).as_dict()

        binary_label = self.models.binary_model.predict([normalized])[0]
        binary_scores = self.models.binary_model.predict_proba([normalized])[0]
        classes = list(self.models.binary_model.classes_)
        binary_confidence = float(max(binary_scores))

        threat_type = None
        threat_confidence = None
        if binary_label == "malicious":
            threat_scores = self.models.threat_model.predict_proba([normalized])[0]
            threat_classes = list(self.models.threat_model.classes_)
            idx = int(threat_scores.argmax())
            threat_type = str(threat_classes[idx])
            threat_confidence = float(threat_scores[idx])

        payload = PredictionResult(
            is_malicious=binary_label == "malicious",
            binary_label=str(binary_label),
            binary_confidence=binary_confidence,
            threat_type=threat_type,
            threat_confidence=threat_confidence,
            signals=signals,
        ).to_dict()

        validate_result_contract(payload)
        self._audit_log(payload)
        return payload

    def _audit_log(self, payload: dict) -> None:
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "binary_label": payload["binary_label"],
            "binary_confidence": payload["binary_confidence"],
            "threat_type": payload["threat_type"],
            "threat_confidence": payload["threat_confidence"],
            "signals": payload["signals"],
        }
        with self.audit_log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

