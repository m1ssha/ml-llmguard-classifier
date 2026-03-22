from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from classifier.src.common.preprocessing import normalize_text
from classifier.src.dataset.schema import LabelSchema


class DatasetValidationError(ValueError):
    pass


@dataclass
class ValidationReport:
    categories: dict[str, int]
    languages: dict[str, int]
    total: int


def _extract_text(sample: dict, sample_id: object) -> str:
    for field in ("text", "prompt", "user_input"):
        value = sample.get(field)
        if value not in (None, ""):
            return str(value)

    raise DatasetValidationError(
        f"Sample {sample_id} missing text input. Expected one of: text, prompt, user_input. "
        f"Available fields: {sorted(sample.keys())}"
    )


def validate_samples(samples: list[dict], schema: LabelSchema | None = None) -> ValidationReport:
    schema = schema or LabelSchema()
    if not samples:
        raise DatasetValidationError("Пустой датасет")

    category_counter = Counter()
    language_counter = Counter()

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

    for category in schema.required_categories:
        if category_counter[category] == 0:
            raise DatasetValidationError(f"Missing required category: {category}")

    for language in schema.required_languages:
        if language_counter[language] == 0:
            raise DatasetValidationError(f"Missing required language coverage: {language}")

    return ValidationReport(categories=dict(category_counter), languages=dict(language_counter), total=len(samples))


def build_distribution_report(report: ValidationReport) -> dict:
    return {
        "total": report.total,
        "categories": report.categories,
        "languages": report.languages,
    }

