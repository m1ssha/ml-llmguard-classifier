from __future__ import annotations

from dataclasses import dataclass


MANDATORY_FIELDS = (
    "id",
    "text",
    "binary_label",
    "threat_type",
    "language",
    "source",
)

REQUIRED_CATEGORIES = (
    "benign",
    "malicious",
    "borderline",
    "obfuscated",
    "near-miss",
)

REQUIRED_LANGUAGES = (
    "ru",
    "en",
    "mixed",
    "translit",
    "distorted",
)


@dataclass(frozen=True)
class LabelSchema:
    mandatory_fields: tuple[str, ...] = MANDATORY_FIELDS
    required_categories: tuple[str, ...] = REQUIRED_CATEGORIES
    required_languages: tuple[str, ...] = REQUIRED_LANGUAGES

