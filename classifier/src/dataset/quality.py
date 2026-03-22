from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re

from classifier.src.common.preprocessing import normalize_text


DEFAULT_SHORTCUT_TRIGGERS = (
    "ignore all previous instructions",
    "system prompt",
    "jailbreak",
    "bypass policy",
)


class ShortcutQualityError(ValueError):
    pass


@dataclass
class ShortcutQualityReport:
    trigger_counts: dict[str, int]
    malicious_count: int
    benign_near_miss_count: int
    adversarial_rewrite_count: int
    max_trigger_share: float


def check_shortcut_patterns(
    samples: list[dict],
    triggers: tuple[str, ...] = DEFAULT_SHORTCUT_TRIGGERS,
    max_trigger_share: float = 0.35,
    min_benign_near_miss: int = 1,
    min_adversarial_rewrite: int = 1,
) -> ShortcutQualityReport:
    malicious_samples = [s for s in samples if str(s.get("binary_label", "")).lower() == "malicious"]
    if not malicious_samples:
        raise ShortcutQualityError("No malicious samples for quality checks")

    counts = Counter()
    benign_near_miss_count = 0
    adversarial_rewrite_count = 0
    for sample in malicious_samples:
        text = normalize_text(str(sample.get("text", "")))
        compact = re.sub(r"\s+", "", text)
        for trigger in triggers:
            if trigger in text:
                counts[trigger] += 1

        if sample.get("category") in {"adversarial-rewrite", "obfuscated", "staged"}:
            adversarial_rewrite_count += 1
        elif any(token in text or token.replace(" ", "") in compact for token in ("i g n o r e", "j a i l b r e a k", "b a s e 6 4", "zero-width")):
            adversarial_rewrite_count += 1

    for sample in samples:
        if str(sample.get("binary_label", "")).lower() != "benign":
            continue
        text = normalize_text(str(sample.get("text", "")))
        if any(
            token in text
            for token in (
                "what is prompt injection",
                "что такое prompt injection",
                "объясни jailbreak",
                "explain jailbreak",
                "анализ угроз llm",
            )
        ):
            benign_near_miss_count += 1

    for trigger, count in counts.items():
        share = count / len(malicious_samples)
        if share > max_trigger_share:
            raise ShortcutQualityError(
                f"Shortcut trigger '{trigger}' is overrepresented ({share:.2%}) and blocks training"
            )

    if benign_near_miss_count < min_benign_near_miss:
        raise ShortcutQualityError(
            f"Benign near-miss coverage is too low ({benign_near_miss_count} < {min_benign_near_miss})"
        )

    if adversarial_rewrite_count < min_adversarial_rewrite:
        raise ShortcutQualityError(
            f"Adversarial rewrite coverage is too low ({adversarial_rewrite_count} < {min_adversarial_rewrite})"
        )

    return ShortcutQualityReport(
        trigger_counts=dict(counts),
        malicious_count=len(malicious_samples),
        benign_near_miss_count=benign_near_miss_count,
        adversarial_rewrite_count=adversarial_rewrite_count,
        max_trigger_share=max_trigger_share,
    )

