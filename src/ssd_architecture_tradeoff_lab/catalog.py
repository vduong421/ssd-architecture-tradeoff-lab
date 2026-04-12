from __future__ import annotations

import itertools
import json
from pathlib import Path


def load_design_space(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def enumerate_candidates(design_space: dict) -> list[dict]:
    keys = list(design_space.keys())
    values = [design_space[key] for key in keys]
    return [dict(zip(keys, combo)) for combo in itertools.product(*values)]

