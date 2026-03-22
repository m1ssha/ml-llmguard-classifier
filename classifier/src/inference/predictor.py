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


@dataclass
class DeploymentProfile:
    name: str = "balanced"
    binary_threshold: float = 0.5
    threat_threshold: float = 0.5
    calibration: dict | None = None


class TwoStagePredictor:
    def __init__(
        self,
        models: InferenceModels,
        audit_log_path: str = "classifier/reports/audit_log.jsonl",
        deployment_profile_path: str | None = None,
    ) -> None:
        self.models = models
        self.audit_log_path = Path(audit_log_path)
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.deployment_profile = self._load_deployment_profile(deployment_profile_path)

    def predict(self, text: str) -> dict:
        normalized = normalize_text(text)
        rule_eval = detect_rule_signals(normalized)
        signals = rule_eval.as_dict()

        binary_label = self.models.binary_model.predict([normalized])[0]
        binary_scores = self.models.binary_model.predict_proba([normalized])[0]
        classes = list(self.models.binary_model.classes_)
        malicious_idx = classes.index("malicious") if "malicious" in classes else int(binary_scores.argmax())
        malicious_score = float(binary_scores[malicious_idx])
        is_malicious = malicious_score >= self.deployment_profile.binary_threshold
        binary_label = "malicious" if is_malicious else "benign"
        binary_confidence = malicious_score

        threat_type = None
        threat_confidence = None
        if is_malicious:
            threat_scores = self.models.threat_model.predict_proba([normalized])[0]
            threat_classes = list(self.models.threat_model.classes_)
            idx = int(threat_scores.argmax())
            threat_candidate = str(threat_classes[idx])
            threat_candidate_confidence = float(threat_scores[idx])
            if threat_candidate_confidence >= self.deployment_profile.threat_threshold:
                threat_type = threat_candidate
            threat_confidence = threat_candidate_confidence

        payload = PredictionResult(
            is_malicious=is_malicious,
            binary_label=str(binary_label),
            binary_confidence=binary_confidence,
            threat_type=threat_type,
            threat_confidence=threat_confidence,
            signals=signals,
            schema_version="v2",
            deployment_profile=self.deployment_profile.name,
            thresholds={
                "binary": self.deployment_profile.binary_threshold,
                "threat": self.deployment_profile.threat_threshold,
            },
            evidence=rule_eval.evidence,
        ).to_dict()

        validate_result_contract(payload)
        self._audit_log(payload)
        return payload

    def _load_deployment_profile(self, deployment_profile_path: str | None) -> DeploymentProfile:
        if not deployment_profile_path:
            return DeploymentProfile()
        path = Path(deployment_profile_path)
        if not path.exists():
            return DeploymentProfile()
        raw = json.loads(path.read_text(encoding="utf-8"))
        return DeploymentProfile(
            name=str(raw.get("name", "balanced")),
            binary_threshold=float(raw.get("binary_threshold", 0.5)),
            threat_threshold=float(raw.get("threat_threshold", 0.5)),
            calibration=raw.get("calibration"),
        )

    def _audit_log(self, payload: dict) -> None:
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "binary_label": payload["binary_label"],
            "binary_confidence": payload["binary_confidence"],
            "threat_type": payload["threat_type"],
            "threat_confidence": payload["threat_confidence"],
            "signals": payload["signals"],
            "deployment_profile": payload.get("deployment_profile"),
            "schema_version": payload.get("schema_version"),
        }
        with self.audit_log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

