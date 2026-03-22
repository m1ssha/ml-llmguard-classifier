from __future__ import annotations

from dataclasses import dataclass
import re


_CONFUSABLES = str.maketrans(
    {
        "а": "a",
        "е": "e",
        "о": "o",
        "р": "p",
        "с": "c",
        "у": "y",
        "х": "x",
    }
)


def _normalize_for_rules(text: str) -> str:
    lowered = text.lower().translate(_CONFUSABLES)
    lowered = lowered.replace("\u200b", "")
    lowered = re.sub(r"[^\w\s]", " ", lowered)
    lowered = re.sub(r"\s+", " ", lowered).strip()
    return lowered


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


@dataclass
class RuleEvaluation:
    signals: RuleSignals
    evidence: dict[str, list[str]]

    def as_dict(self) -> dict:
        return self.signals.as_dict()


def _find_matches(text: str, patterns: tuple[str, ...]) -> list[str]:
    compact = text.replace(" ", "")
    matched = []
    for pattern in patterns:
        if pattern in text or pattern.replace(" ", "") in compact:
            matched.append(pattern)
    return matched


def detect_rule_signals(text: str) -> RuleEvaluation:
    normalized = _normalize_for_rules(text)
    prompt_leakage_matches = _find_matches(
        normalized,
        (
            "system prompt",
            "show prompt",
            "reveal instruction",
            "скрытые инструкции",
        ),
    )
    role_override_matches = _find_matches(
        normalized,
        (
            "you are now",
            "ignore previous",
            "act as",
            "теперь ты",
            "игнорируй предыдущие",
            "i g n o r e",
        ),
    )
    bypass_matches = _find_matches(
        normalized,
        (
            "bypass",
            "jailbreak",
            "policy bypass",
            "обойди ограничения",
            "j a i l b r e a k",
        ),
    )
    obfuscation_matches = _find_matches(
        normalized,
        (
            "b64",
            "base64",
            "rot13",
            "zero width",
            "unicode confusable",
            "b a s e 6 4",
        ),
    )

    signals = RuleSignals(
        prompt_leakage=1.0 if prompt_leakage_matches else 0.0,
        role_override=1.0 if role_override_matches else 0.0,
        bypass=1.0 if bypass_matches else 0.0,
        obfuscation=1.0 if obfuscation_matches else 0.0,
    )
    evidence = {
        "prompt_leakage": prompt_leakage_matches,
        "role_override": role_override_matches,
        "bypass": bypass_matches,
        "obfuscation": obfuscation_matches,
    }
    return RuleEvaluation(signals=signals, evidence=evidence)

