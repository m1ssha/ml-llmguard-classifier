from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import json
import random

import numpy as np


@dataclass
class ReproConfig:
    seed: int = 42
    experiment_name: str = "default"
    output_root: str = "classifier/experiments"


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def create_experiment_dir(config: ReproConfig) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = Path(config.output_root) / f"{config.experiment_name}_{timestamp}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_config_snapshot(config: ReproConfig, output_dir: Path, extra: dict | None = None) -> Path:
    snapshot = asdict(config)
    snapshot["created_at_utc"] = datetime.now(timezone.utc).isoformat()
    if extra:
        snapshot["extra"] = extra
    snapshot_path = output_dir / "config_snapshot.json"
    snapshot_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    return snapshot_path

