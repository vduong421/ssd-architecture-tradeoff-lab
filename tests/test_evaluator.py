import unittest
from pathlib import Path

from src.ssd_architecture_tradeoff_lab.catalog import load_design_space
from src.ssd_architecture_tradeoff_lab.evaluator import evaluate_design_space


class EvaluatorTests(unittest.TestCase):
    def test_tradeoff_lab_ranks_candidates(self) -> None:
        sample = Path(__file__).resolve().parents[1] / "samples" / "design_space.json"
        payload = load_design_space(sample)
        result = evaluate_design_space(payload, top_n=3)

        self.assertGreater(result["candidate_count"], 10)
        self.assertEqual(len(result["top_candidates"]), 3)
        self.assertIn("validation_ready_count", result["summary"])
        self.assertIn("ai_focus_area", result["summary"])
        self.assertIn("validation_readiness", result["top_candidates"][0]["metrics"])
        self.assertGreaterEqual(
            result["top_candidates"][0]["weighted_score"],
            result["top_candidates"][1]["weighted_score"],
        )


if __name__ == "__main__":
    unittest.main()
