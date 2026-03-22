from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from datasets import load_dataset
import pandas as pd


SplitName = Literal["train", "validation", "test"]

HF_DATASET_ALIAS = "neuralchemy/Prompt-injection-dataset"
HH_RLHF_DATASET_ALIAS = "Anthropic/hh-rlhf"

DEFAULT_SPLITS: dict[SplitName, str] = {
    "train": "train",
    "validation": "validation",
    "test": "test",
}

TEXT_COLUMN_ALIASES = ("text", "prompt", "user_input", "chosen", "rejected")
LABEL_COLUMN_ALIASES = ("label", "binary_label", "is_malicious", "target")
PREFERENCE_COLUMN_ALIASES = ("chosen", "rejected")


@dataclass(frozen=True)
class HFDatasetSource:
    name: str
    dataset_id: str
    split_map: dict[SplitName, str] = field(default_factory=lambda: dict(DEFAULT_SPLITS))
    revision: str | None = None
    mapping_policy: str = "label_alias"
    role: str = "attack_primary"


@dataclass(frozen=True)
class MultiSourceDatasetBundle:
    splits: dict[SplitName, pd.DataFrame]
    source_metadata: dict[str, dict]


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


def _to_binary_label_name(value: object) -> str:
    return "malicious" if _normalize_binary_label(value) == 1 else "benign"


def _infer_language(text: str) -> str:
    has_cyr = any("а" <= ch.lower() <= "я" for ch in text)
    has_lat = any("a" <= ch.lower() <= "z" for ch in text)
    if has_cyr and has_lat:
        return "mixed"
    if has_cyr:
        return "ru"
    if any(ch.isalpha() for ch in text):
        return "en"
    return "distorted"


def _ensure_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    if "prompt" not in result.columns and "user_input" in result.columns:
        result["prompt"] = result["user_input"]
    if "prompt" not in result.columns and "text" in result.columns:
        result["prompt"] = result["text"]
    if "prompt" not in result.columns and "chosen" in result.columns:
        result["prompt"] = result["chosen"]
    if "prompt" not in result.columns and "rejected" in result.columns:
        result["prompt"] = result["rejected"]

    if "text" not in result.columns and "prompt" in result.columns:
        result["text"] = result["prompt"]
    if "text" not in result.columns and "user_input" in result.columns:
        result["text"] = result["user_input"]
    if "text" not in result.columns and "chosen" in result.columns:
        result["text"] = result["chosen"]
    if "text" not in result.columns and "rejected" in result.columns:
        result["text"] = result["rejected"]

    if not any(column in result.columns for column in TEXT_COLUMN_ALIASES):
        raise ValueError(
            "Dataset must contain at least one text column: text or prompt "
            "(aliases: user_input, chosen, rejected). "
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


def _load_hf_split_frame(dataset_id: str, split_name: str, revision: str | None = None) -> pd.DataFrame:
    try:
        kwargs = {"split": split_name}
        if revision:
            kwargs["revision"] = revision
        dataset = load_dataset(dataset_id, **kwargs)
    except Exception as error:  # noqa: BLE001
        raise ValueError(
            f"Failed to load split '{split_name}' from dataset '{dataset_id}'"
            + (f" at revision '{revision}'" if revision else "")
            + "."
        ) from error
    return _normalize_dataset_frame(dataset.to_pandas())


def _build_canonical_label_source_rows(frame: pd.DataFrame, source: HFDatasetSource, split: SplitName) -> pd.DataFrame:
    result = frame.copy()
    label_column = next((name for name in LABEL_COLUMN_ALIASES if name in result.columns), None)
    if label_column is None and "label" not in result.columns:
        raise ValueError(
            f"Source '{source.name}' requires binary labels but none of {LABEL_COLUMN_ALIASES} were found. "
            f"Available columns: {list(result.columns)}"
        )

    if "label" in result.columns:
        result["binary_label"] = result["label"].map(_to_binary_label_name)
    else:
        result["binary_label"] = result[label_column].map(_to_binary_label_name)

    result["text"] = result["text"].astype(str)
    result["prompt"] = result["text"]
    if "id" not in result.columns:
        result["id"] = [f"{source.name}_{split}_{idx}" for idx in range(len(result))]
    else:
        result["id"] = result["id"].astype(str)

    result["language"] = result.get("language", result["text"].map(_infer_language)).astype(str)
    result["source"] = result.get("source", f"hf:{source.name}:{split}")
    result["dataset_id"] = source.dataset_id
    result["split_role"] = split
    result["dataset_revision"] = source.revision or "latest"
    result["mapping_policy"] = source.mapping_policy
    result["origin_field"] = "text"
    result["category"] = result["binary_label"].map(lambda x: "staged" if x == "malicious" else "benign")
    result["threat_type"] = result["binary_label"].map(lambda x: "prompt_injection" if x == "malicious" else "none")
    return result


def _build_hh_policy_a_rows(frame: pd.DataFrame, source: HFDatasetSource, split: SplitName) -> pd.DataFrame:
    rows: list[dict] = []
    for idx, row in frame.iterrows():
        base_id = str(row.get("id", f"{source.name}_{split}_{idx}"))
        for origin_field, binary_label, category in (
            ("chosen", "benign", "near-miss"),
            ("rejected", "malicious", "adversarial-rewrite"),
        ):
            text = row.get(origin_field)
            if text in (None, ""):
                continue
            text_str = str(text)
            rows.append(
                {
                    "id": f"{base_id}:{origin_field}",
                    "text": text_str,
                    "prompt": text_str,
                    "binary_label": binary_label,
                    "threat_type": "prompt_injection" if binary_label == "malicious" else "none",
                    "language": _infer_language(text_str),
                    "source": f"hf:{source.name}:{split}",
                    "dataset_id": source.dataset_id,
                    "split_role": split,
                    "dataset_revision": source.revision or "latest",
                    "mapping_policy": source.mapping_policy,
                    "origin_field": origin_field,
                    "category": category,
                }
            )

    if not rows:
        raise ValueError(
            f"Source '{source.name}' expects chosen/rejected columns for policy '{source.mapping_policy}'. "
            f"Available columns: {list(frame.columns)}"
        )

    return pd.DataFrame(rows)


def normalize_source_split_to_canonical(source: HFDatasetSource, split: SplitName, frame: pd.DataFrame) -> pd.DataFrame:
    if source.mapping_policy == "chosen_rejected_policy_a":
        return _build_hh_policy_a_rows(frame, source=source, split=split)
    return _build_canonical_label_source_rows(frame, source=source, split=split)


def default_source_registry(
    prompt_injection_dataset_id: str = HF_DATASET_ALIAS,
    hh_rlhf_dataset_id: str = HH_RLHF_DATASET_ALIAS,
) -> list[HFDatasetSource]:
    return [
        HFDatasetSource(
            name="prompt_injection",
            dataset_id=prompt_injection_dataset_id,
            split_map=dict(DEFAULT_SPLITS),
            mapping_policy="label_alias",
            role="attack_primary",
        ),
        HFDatasetSource(
            name="hh_rlhf",
            dataset_id=hh_rlhf_dataset_id,
            split_map={"train": "train", "validation": "test", "test": "test"},
            mapping_policy="chosen_rejected_policy_a",
            role="alignment_aux",
        ),
    ]


def load_source_split(source: HFDatasetSource, split: SplitName) -> pd.DataFrame:
    if split not in source.split_map:
        raise ValueError(f"Unknown split '{split}'. Available: {list(source.split_map.keys())}")
    source_split = source.split_map[split]
    frame = _load_hf_split_frame(source.dataset_id, source_split, revision=source.revision)
    return normalize_source_split_to_canonical(source=source, split=split, frame=frame)


def load_multisource_canonical_dataset(
    sources: list[HFDatasetSource] | None = None,
) -> MultiSourceDatasetBundle:
    source_list = sources or default_source_registry()
    collected: dict[SplitName, list[pd.DataFrame]] = {"train": [], "validation": [], "test": []}

    for source in source_list:
        for split in ("train", "validation", "test"):
            collected[split].append(load_source_split(source, split))

    merged_splits = {
        split: pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        for split, frames in collected.items()
    }
    metadata = {
        source.name: {
            "dataset_id": source.dataset_id,
            "revision": source.revision or "latest",
            "mapping_policy": source.mapping_policy,
            "role": source.role,
            "split_map": source.split_map,
        }
        for source in source_list
    }
    return MultiSourceDatasetBundle(splits=merged_splits, source_metadata=metadata)


def load_hf_prompt_injection_split(
    split: SplitName,
    dataset_id: str = HF_DATASET_ALIAS,
    splits: dict[SplitName, str] | None = None,
) -> pd.DataFrame:
    """Загружает один split из Hugging Face Hub и нормализует схему колонок."""
    split_map = splits or DEFAULT_SPLITS
    if split not in split_map:
        raise ValueError(f"Unknown split '{split}'. Available: {list(split_map.keys())}")
    hf_split = split_map[split]
    return _load_hf_split_frame(dataset_id=dataset_id, split_name=hf_split)


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

