from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULT = APP_DIR / "results" / "xhd_goal5350_functional_parity_matrix_amendment.json"
GOAL5348 = APP_DIR / "results" / "xhd_goal5348_witness_parity_entrypoint_route_audit.json"
GOAL5349 = APP_DIR / "results" / "xhd_goal5349_hd_exec_variant_value_surface.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class Goal5350XhdFunctionalParityMatrixAmendmentTest(unittest.TestCase):
    def test_amendment_keeps_full_functional_parity_false(self) -> None:
        result = load_json(RESULT)

        self.assertFalse(result["amended_interpretation"]["full_functional_parity_ready"])
        self.assertFalse(result["claim_boundary"]["full_xhd_paper_reproduction_claimed"])
        self.assertFalse(result["claim_boundary"]["full_functional_parity_claimed"])
        self.assertFalse(result["claim_boundary"]["exact_paper_dataset_identity_claimed"])
        self.assertFalse(result["claim_boundary"]["performance_ratio_claimed"])
        self.assertIn("exact paper input artifacts/provenance", result["remaining_major_blockers"])

    def test_witness_status_is_split_between_entrypoint_and_fast_scalar(self) -> None:
        result = load_json(RESULT)
        witness = next(item for item in result["amended_feature_status"] if item["feature"] == "Exact per-source nearest witness output")
        goal5348 = load_json(GOAL5348)

        self.assertIn("covered_for_hd_exec_exact_witness_entrypoint", witness["amended_status"])
        self.assertTrue(
            goal5348["goal5347_refinement"]["refined_interpretation"][
                "not_a_blocker_for_hd_exec_default_3d_gpu_value_plus_witness_entrypoint_on_existing_level_b_artifacts"
            ]
        )
        self.assertIn("fast-scalar", " ".join(witness["remaining_gap"]))
        self.assertIn("approximate", " ".join(witness["remaining_gap"]))

    def test_variant_status_is_value_surface_only(self) -> None:
        result = load_json(RESULT)
        variant = next(item for item in result["amended_feature_status"] if item["feature"] == "hd_exec-compatible CLI and JSON output")
        goal5349 = load_json(GOAL5349)

        self.assertEqual(
            goal5349["value_surface_contract"]["non_rt_variant_status"],
            "author_variant_value_compatible_route_only",
        )
        self.assertIn("variant names eb/nn/itk/clover/rt", " ".join(variant["covered_now"]))
        self.assertIn("non-rt variant-specific algorithms are not reproduced", variant["remaining_gap"])
        self.assertFalse(result["claim_boundary"]["author_variant_algorithm_equivalence_claimed"])

    def test_next_targets_are_real_functional_blockers_not_route_micro_tuning(self) -> None:
        result = load_json(RESULT)
        targets = {item["target"] for item in result["recommended_next_functional_targets"]}

        self.assertIn("author variant algorithm/performance surface", targets)
        self.assertIn("author-equivalent pruning / EB semantics", targets)
        self.assertIn("load-balance / heavy-cell offload behavior", targets)
        self.assertNotIn("inline threshold micro-tuning", targets)


if __name__ == "__main__":
    unittest.main()
