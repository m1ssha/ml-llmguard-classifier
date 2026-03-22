from __future__ import annotations

import re
from dataclasses import dataclass


_WHITESPACE_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class PreprocessConfig:
    lower: bool = True
    strip: bool = True
    collapse_whitespace: bool = True


def normalize_text(text: str, config: PreprocessConfig | None = None) -> str:
    """Единый preprocessing для train/inference."""
    config = config or PreprocessConfig()
    result = text
    if config.strip:
        result = result.strip()
    if config.lower:
        result = result.lower()
    if config.collapse_whitespace:
        result = _WHITESPACE_RE.sub(" ", result)
    return result


def preprocess_batch(texts: list[str], config: PreprocessConfig | None = None) -> list[str]:
    return [normalize_text(text, config=config) for text in texts]

