from __future__ import annotations

from typing import Literal

import pandas as pd
from datasets import load_dataset


SplitName = Literal["train", "validation", "test"]

# Backward-compatible export used by classifier.src.dataset.__init__
DEFAULT_SPLITS: dict[SplitName, str] = {
    "train": "train",
    "validation": "validation",
    "test": "test",
}

def load_hf_prompt_injection_split(
    split: SplitName,
    dataset_id: str = "imoxto/prompt_injection_cleaned_dataset",
) -> pd.DataFrame:
    """Загружает один split датасета из Hugging Face Hub через `datasets.load_dataset`."""
    if split not in DEFAULT_SPLITS:
        raise ValueError(f"Unknown split '{split}'. Available: {list(DEFAULT_SPLITS.keys())}")

    ds = load_dataset(dataset_id, split=DEFAULT_SPLITS[split])
    return ds.to_pandas()


def load_hf_prompt_injection_dataset(
    dataset_id: str = "imoxto/prompt_injection_cleaned_dataset",
) -> dict[SplitName, pd.DataFrame]:
    """Загружает train/validation/test в виде словаря DataFrame."""
    ds = load_dataset(dataset_id)
    return {
        "train": ds["train"].to_pandas(),
        "validation": ds["validation"].to_pandas(),
        "test": ds["test"].to_pandas(),
    }

