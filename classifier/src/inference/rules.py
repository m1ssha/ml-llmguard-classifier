from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RuleSignals:
    prompt_leakage: float
    role_override: float
    bypass: float
    obfuscation: float

    def as_dict(self) -> dict:
        return {
            "prompt_leakage": self.prompt_leakage,
            "role_override": self.role_override,
            "bypass": self.bypass,
            "obfuscation": self.obfuscation,
        }


def detect_rule_signals(text: str) -> RuleSignals:
    lowered = text.lower()
    return RuleSignals(
        prompt_leakage=1.0 if "system prompt" in lowered or "show prompt" in lowered else 0.0,
        role_override=1.0 if "you are now" in lowered or "ignore previous" in lowered else 0.0,
        bypass=1.0 if "bypass" in lowered or "jailbreak" in lowered else 0.0,
        obfuscation=1.0 if any(token in lowered for token in ("b64", "base64", "rot13", "zero-width")) else 0.0,
    )

