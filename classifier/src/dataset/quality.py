from __future__ import annotations

from collections import Counter
from dataclasses import dataclass


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
    max_trigger_share: float


def check_shortcut_patterns(
    samples: list[dict],
    triggers: tuple[str, ...] = DEFAULT_SHORTCUT_TRIGGERS,
    max_trigger_share: float = 0.35,
) -> ShortcutQualityReport:
    malicious_samples = [s for s in samples if str(s.get("binary_label", "")).lower() == "malicious"]
    if not malicious_samples:
        raise ShortcutQualityError("No malicious samples for quality checks")

    counts = Counter()
    for sample in malicious_samples:
        text = str(sample.get("text", "")).lower()
        for trigger in triggers:
            if trigger in text:
                counts[trigger] += 1

    for trigger, count in counts.items():
        share = count / len(malicious_samples)
        if share > max_trigger_share:
            raise ShortcutQualityError(
                f"Shortcut trigger '{trigger}' is overrepresented ({share:.2%}) and blocks training"
            )

    return ShortcutQualityReport(
        trigger_counts=dict(counts),
        malicious_count=len(malicious_samples),
        max_trigger_share=max_trigger_share,
    )

