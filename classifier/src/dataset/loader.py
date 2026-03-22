from __future__ import annotations

from typing import Literal

import pandas as pd


SplitName = Literal["train", "validation", "test"]

DEFAULT_SPLITS: dict[SplitName, str] = {
    "train": "core/train-00000-of-00001.parquet",
    "validation": "core/validation-00000-of-00001.parquet",
    "test": "core/test-00000-of-00001.parquet",
}


def load_hf_prompt_injection_split(
    split: SplitName,
    dataset_id: str = "neuralchemy/Prompt-injection-dataset",
    splits: dict[SplitName, str] | None = None,
) -> pd.DataFrame:
    """Загружает один split parquet напрямую из Hugging Face Hub через `hf://`.

    Пример пути: `hf://datasets/neuralchemy/Prompt-injection-dataset/core/train-00000-of-00001.parquet`
    """
    split_map = splits or DEFAULT_SPLITS
    if split not in split_map:
        raise ValueError(f"Unknown split '{split}'. Available: {list(split_map.keys())}")

    parquet_path = f"hf://datasets/{dataset_id}/{split_map[split]}"
    return pd.read_parquet(parquet_path)


def load_hf_prompt_injection_dataset(
    dataset_id: str = "neuralchemy/Prompt-injection-dataset",
    splits: dict[SplitName, str] | None = None,
) -> dict[SplitName, pd.DataFrame]:
    """Загружает train/validation/test в виде словаря DataFrame."""
    split_map = splits or DEFAULT_SPLITS
    return {
        "train": load_hf_prompt_injection_split("train", dataset_id=dataset_id, splits=split_map),
        "validation": load_hf_prompt_injection_split("validation", dataset_id=dataset_id, splits=split_map),
        "test": load_hf_prompt_injection_split("test", dataset_id=dataset_id, splits=split_map),
    }

