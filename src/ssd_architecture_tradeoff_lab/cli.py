from __future__ import annotations

import argparse
import json

from .catalog import load_design_space
from .evaluator import evaluate_design_space


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate SSD architecture tradeoffs.")
    parser.add_argument("--input", required=True, help="Path to design-space JSON.")
    parser.add_argument("--top", type=int, default=5, help="Number of top candidates to display.")
    args = parser.parse_args()

    payload = load_design_space(args.input)
    result = evaluate_design_space(payload, top_n=args.top)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

