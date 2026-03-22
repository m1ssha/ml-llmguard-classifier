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


def validate_samples(samples: list[dict], schema: LabelSchema | None = None) -> ValidationReport:
    schema = schema or LabelSchema()
    if not samples:
        raise DatasetValidationError("Пустой датасет")

    category_counter = Counter()
    language_counter = Counter()

    for sample in samples:
        for field in schema.mandatory_fields:
            if field not in sample or sample[field] in (None, ""):
                raise DatasetValidationError(f"Sample {sample.get('id', '<unknown>')} missing field: {field}")

        normalized_text = normalize_text(str(sample["text"]))
        if not normalized_text:
            raise DatasetValidationError(f"Sample {sample['id']} has empty normalized text")

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

