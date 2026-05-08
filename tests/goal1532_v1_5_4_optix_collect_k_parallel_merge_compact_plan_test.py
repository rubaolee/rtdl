from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "reports" / "goal1532_v1_5_4_optix_collect_k_parallel_merge_compact_plan_2026-05-08.md"


class Goal1532V154OptixCollectKParallelMergeCompactPlanTest(unittest.TestCase):
    def test_plan_is_grounded_in_measured_prior_goals(self) -> None:
        text = PLAN.read_text(encoding="utf-8")

        self.assertIn("Goal1506 accepted baseline", text)
        self.assertIn("Goal1529 one-pass merge", text)
        self.assertIn("Goal1530 batched merge-level launch", text)
        self.assertIn("Goal1531 per-level profiling", text)
        self.assertIn("10.7143", text)

    def test_plan_preserves_contract_and_claim_boundary(self) -> None:
        text = PLAN.read_text(encoding="utf-8")

        self.assertIn("Output rows are sorted unique", text)
        self.assertIn("exact number of unique merged rows", text)
        self.assertIn("Rows written to output are bounded by `output_capacity`", text)
        self.assertIn("does not authorize public speedup wording", text)
        self.assertIn("does not promote `COLLECT_K_BOUNDED` to stable", text)

    def test_plan_names_next_prototype_gate(self) -> None:
        text = PLAN.read_text(encoding="utf-8")

        self.assertIn("RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_MERGE", text)
        self.assertIn("Build succeeds on the NVIDIA pod", text)
        self.assertIn("If the prototype regresses", text)


if __name__ == "__main__":
    unittest.main()
