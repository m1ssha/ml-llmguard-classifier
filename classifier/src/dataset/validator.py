from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re

from classifier.src.common.preprocessing import normalize_text
from classifier.src.dataset.schema import LabelSchema


class DatasetValidationError(ValueError):
    pass


@dataclass
class ValidationReport:
    categories: dict[str, int]
    languages: dict[str, int]
    adversarial_holdouts: dict[str, int]
    total: int


_HOLDOUT_PATTERNS = {
    "obfuscation": ("base64", "b64", "rot13", "zero-width", "z e r o", "i g n o r e"),
    "policy_bypass": ("bypass", "ignore", "jailbreak", "override"),
    "multilingual_transfer": ("привет", "hello", "как", "translate", "переведи", "ассистент"),
    "benign_security_discussion": ("what is prompt injection", "что такое prompt injection", "объясни jailbreak"),
}


def infer_holdout_slice(text: str, binary_label: str, language: str) -> str | None:
    lowered = normalize_text(text)
    compact = re.sub(r"\s+", "", lowered)
    if any(token in lowered or token.replace(" ", "") in compact for token in _HOLDOUT_PATTERNS["obfuscation"]):
        return "obfuscation"
    if any(token in lowered for token in _HOLDOUT_PATTERNS["policy_bypass"]):
        return "policy_bypass"
    if language in {"mixed", "translit"} or any(token in lowered for token in _HOLDOUT_PATTERNS["multilingual_transfer"]):
        return "multilingual_transfer"
    if binary_label == "benign" and any(token in lowered for token in _HOLDOUT_PATTERNS["benign_security_discussion"]):
        return "benign_security_discussion"
    return None


def _extract_text(sample: dict, sample_id: object) -> str:
    for field in ("text", "prompt", "user_input"):
        value = sample.get(field)
        if value not in (None, ""):
            return str(value)

    raise DatasetValidationError(
        f"Sample {sample_id} missing text input. Expected one of: text, prompt, user_input. "
        f"Available fields: {sorted(sample.keys())}"
    )


def validate_samples(
    samples: list[dict],
    schema: LabelSchema | None = None,
    strict_adversarial: bool = False,
) -> ValidationReport:
    schema = schema or LabelSchema()
    if not samples:
        raise DatasetValidationError("Пустой датасет")

    category_counter = Counter()
    language_counter = Counter()
    holdout_counter = Counter()

    for sample in samples:
        sample_id = sample.get("id", "<unknown>")
        for field in schema.mandatory_fields:
            if field not in sample or sample[field] in (None, ""):
                raise DatasetValidationError(f"Sample {sample_id} missing field: {field}")

        if not any(sample.get(field) not in (None, "") for field in schema.mandatory_text_any_of):
            raise DatasetValidationError(
                f"Sample {sample_id} missing text field. Expected one of: {schema.mandatory_text_any_of}"
            )

        normalized_text = normalize_text(_extract_text(sample, sample_id))
        if not normalized_text:
            raise DatasetValidationError(f"Sample {sample_id} has empty normalized text")

        category = str(sample.get("category", sample["binary_label"]))
        language = str(sample["language"])
        category_counter[category] += 1
        language_counter[language] += 1

        holdout = sample.get("robustness_slice")
        if holdout in (None, ""):
            holdout = infer_holdout_slice(normalized_text, str(sample.get("binary_label", "")), language)
        if holdout:
            holdout_counter[str(holdout)] += 1

    for category in schema.required_categories:
        if category_counter[category] == 0:
            raise DatasetValidationError(f"Missing required category: {category}")

    for language in schema.required_languages:
        if language_counter[language] == 0:
            raise DatasetValidationError(f"Missing required language coverage: {language}")

    if strict_adversarial:
        for holdout in schema.required_adversarial_holdouts:
            if holdout_counter[holdout] == 0:
                raise DatasetValidationError(f"Missing required adversarial holdout slice: {holdout}")

    return ValidationReport(
        categories=dict(category_counter),
        languages=dict(language_counter),
        adversarial_holdouts=dict(holdout_counter),
        total=len(samples),
    )


def build_adversarial_holdout_splits(samples: list[dict], schema: LabelSchema | None = None) -> dict[str, list[dict]]:
    schema = schema or LabelSchema()
    splits: dict[str, list[dict]] = {name: [] for name in schema.required_adversarial_holdouts}
    for sample in samples:
        sample_id = sample.get("id", "<unknown>")
        text = _extract_text(sample, sample_id)
        language = str(sample.get("language", ""))
        binary_label = str(sample.get("binary_label", ""))
        holdout = sample.get("robustness_slice") or infer_holdout_slice(text, binary_label, language)
        if holdout in splits:
            splits[str(holdout)].append(sample)
    return splits


def build_distribution_report(report: ValidationReport) -> dict:
    return {
        "total": report.total,
        "categories": report.categories,
        "languages": report.languages,
        "adversarial_holdouts": report.adversarial_holdouts,
    }

