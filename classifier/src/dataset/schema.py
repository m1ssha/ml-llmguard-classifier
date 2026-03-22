from __future__ import annotations

from dataclasses import dataclass


MANDATORY_FIELDS = (
    "id",
    "binary_label",
    "threat_type",
    "language",
    "source",
)

MANDATORY_TEXT_ANY_OF = (
    "text",
    "prompt",
)

REQUIRED_CATEGORIES = (
    "benign",
    "malicious",
    "borderline",
    "obfuscated",
    "near-miss",
    "staged",
    "adversarial-rewrite",
)

REQUIRED_LANGUAGES = (
    "ru",
    "en",
    "mixed",
    "translit",
    "distorted",
)

REQUIRED_ADVERSARIAL_HOLDOUTS = (
    "obfuscation",
    "policy_bypass",
    "multilingual_transfer",
    "benign_security_discussion",
)


@dataclass(frozen=True)
class LabelSchema:
    mandatory_fields: tuple[str, ...] = MANDATORY_FIELDS
    mandatory_text_any_of: tuple[str, ...] = MANDATORY_TEXT_ANY_OF
    required_categories: tuple[str, ...] = REQUIRED_CATEGORIES
    required_languages: tuple[str, ...] = REQUIRED_LANGUAGES
    required_adversarial_holdouts: tuple[str, ...] = REQUIRED_ADVERSARIAL_HOLDOUTS

