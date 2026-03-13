from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Paths:
    project_root: Path = Path(__file__).resolve().parents[2]
    data_raw: Path = project_root / "data" / "raw"
    data_processed: Path = project_root / "data" / "processed"
    data_tokenized: Path = project_root / "data" / "tokenized"
    checkpoints: Path = project_root / "checkpoints"
    logs: Path = project_root / "logs"


@dataclass(frozen=True)
class TrainingConfig:
    seed: int = 42
    model_size: str = "30M"
    context_length: int = 512
    micro_batch_size: int = 4
    grad_accum_step: int = 32
    max_steps: int = 1000
    lr: float = 3e-4
    weight_decay: float = 0.1
    warmup_steps = 100
    grad_clip: float = 1.0