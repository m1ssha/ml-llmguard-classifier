from __future__ import annotations

from typing import Literal

from datasets import load_dataset
import pandas as pd


SplitName = Literal["train", "validation", "test"]

HF_DATASET_ALIAS = "neuralchemy/Prompt-injection-dataset"

DEFAULT_SPLITS: dict[SplitName, str] = {
    "train": "train",
    "validation": "validation",
    "test": "test",
}

TEXT_COLUMN_ALIASES = ("text", "prompt", "user_input")
LABEL_COLUMN_ALIASES = ("label", "binary_label", "is_malicious", "target")


def _normalize_binary_label(value: object) -> int:
    if isinstance(value, bool):
        return 1 if value else 0

    if isinstance(value, (int, float)):
        int_value = int(value)
        if int_value in (0, 1):
            return int_value
        raise ValueError(f"Unsupported numeric label value: {value}")

    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "malicious", "attack", "prompt_injection", "yes"}:
        return 1
    if normalized in {"0", "false", "benign", "no"}:
        return 0
    raise ValueError(f"Unsupported label value: {value}")


def _ensure_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    if "prompt" not in result.columns and "user_input" in result.columns:
        result["prompt"] = result["user_input"]
    if "prompt" not in result.columns and "text" in result.columns:
        result["prompt"] = result["text"]

    if "text" not in result.columns and "prompt" in result.columns:
        result["text"] = result["prompt"]
    if "text" not in result.columns and "user_input" in result.columns:
        result["text"] = result["user_input"]

    if not any(column in result.columns for column in TEXT_COLUMN_ALIASES):
        raise ValueError(
            "Dataset must contain at least one text column: text or prompt (aliases: user_input). "
            f"Available columns: {list(result.columns)}"
        )

    return result


def _ensure_label_column(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    label_column = next((name for name in LABEL_COLUMN_ALIASES if name in result.columns), None)
    if label_column is None:
        return result

    try:
        result["label"] = result[label_column].map(_normalize_binary_label)
    except ValueError as error:
        raise ValueError(
            "Failed to normalize label column. Supported values: 0/1, true/false, bool/int/str. "
            f"Source column: {label_column}"
        ) from error

    return result


def _normalize_dataset_frame(df: pd.DataFrame) -> pd.DataFrame:
    with_text = _ensure_text_columns(df)
    return _ensure_label_column(with_text)


def load_hf_prompt_injection_split(
    split: SplitName,
    dataset_id: str = HF_DATASET_ALIAS,
    splits: dict[SplitName, str] | None = None,
) -> pd.DataFrame:
    """Загружает один split из Hugging Face Hub и нормализует схему колонок."""
    split_map = splits or DEFAULT_SPLITS
    if split not in split_map:
        raise ValueError(f"Unknown split '{split}'. Available: {list(split_map.keys())}")

    try:
        hf_split = split_map[split]
        dataset = load_dataset(dataset_id, split=hf_split)
    except Exception as error:  # noqa: BLE001
        raise ValueError(
            f"Failed to load split '{split}' (HF split: '{split_map[split]}') "
            f"from dataset '{dataset_id}'."
        ) from error

    return _normalize_dataset_frame(dataset.to_pandas())


def load_hf_prompt_injection_dataset(
    dataset_id: str = HF_DATASET_ALIAS,
    splits: dict[SplitName, str] | None = None,
) -> dict[SplitName, pd.DataFrame]:
    """Загружает train/validation/test в виде словаря DataFrame."""
    split_map = splits or DEFAULT_SPLITS
    return {
        "train": load_hf_prompt_injection_split("train", dataset_id=dataset_id, splits=split_map),
        "validation": load_hf_prompt_injection_split("validation", dataset_id=dataset_id, splits=split_map),
        "test": load_hf_prompt_injection_split("test", dataset_id=dataset_id, splits=split_map),
    }

