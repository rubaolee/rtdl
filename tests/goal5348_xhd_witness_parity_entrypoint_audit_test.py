import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results" / "xhd_goal5348_witness_parity_entrypoint_route_audit.json"
RUNNER = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts" / "run_xhd_rtdl_hd_exec.py"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class Goal5348XhdWitnessParityEntrypointAuditTest(unittest.TestCase):
    def test_auto_3d_gpu_entrypoint_defaults_to_exact_witness_route(self):
        result = load_json(RESULT)
        runner_text = RUNNER.read_text(encoding="utf-8")

        self.assertEqual(
            result["audited_entrypoint"]["hd_exec_default_3d_gpu_route"],
            "cell-mbr-exact-witness",
        )
        self.assertTrue(result["audited_entrypoint"]["hd_exec_default_3d_gpu_per_source_witness_exact"])
        self.assertIn('return "cell-mbr-exact-witness"', runner_text)
        self.assertIn(
            "directed_input1_to_input2_per_source_witness_exact_seed_route",
            runner_text,
        )
        self.assertIn(
            "directed_input1_to_input2_witness_may_be_approximate_for_fast_scalar",
            runner_text,
        )

    def test_modelnet_all400_entrypoint_evidence_is_exact_witness(self):
        result = load_json(RESULT)
        modelnet = result["exact_witness_entrypoint_evidence"]["modelnet40_all400"]
        artifact = ROOT / modelnet["artifact"]
        payload = load_json(artifact)

        self.assertEqual(modelnet["route_label"], "cell-mbr-exact-witness")
        self.assertEqual(payload["route_label"], "cell-mbr-exact-witness")
        self.assertEqual(payload["selected_case_count"], 400)
        self.assertEqual(payload["matched_case_count"], 400)
        self.assertEqual(payload["failed_case_count"], 0)
        self.assertTrue(payload["all_cases_matched"])
        self.assertTrue(all(case["per_source_witness_exact"] for case in payload["cases"]))
        self.assertTrue(modelnet["all_cases_per_source_witness_exact"])

    def test_graphics_representative_entrypoint_evidence_is_exact_witness(self):
        result = load_json(RESULT)
        cases = result["exact_witness_entrypoint_evidence"]["stanford_graphics_representatives"]
        self.assertEqual(len(cases), 4)

        for case in cases:
            with self.subTest(case=case["name"]):
                payload = load_json(ROOT / case["artifact"])
                self.assertEqual(payload["RTDL"]["route_label"], "cell-mbr-exact-witness")
                self.assertEqual(payload["RTDL"]["route"]["route_label"], "cell-mbr-exact-witness")
                self.assertTrue(payload["RTDL"]["route"]["per_source_witness_exact"])
                self.assertEqual(
                    payload["RTDL"]["route"]["witness_contract"],
                    "directed_input1_to_input2_per_source_witness_exact_seed_route",
                )
                self.assertEqual(case["hd_result"], payload["HDResult"])
                self.assertEqual(case["point_count_a"], payload["RTDL"]["point_count_a"])
                self.assertEqual(case["point_count_b"], payload["RTDL"]["point_count_b"])

    def test_fast_scalar_route_is_exact_value_not_exact_witness(self):
        result = load_json(RESULT)
        fast = result["fast_scalar_route_evidence"]
        payload = load_json(ROOT / fast["artifact"])
        measured = payload["cases"][0]["rtdl_route"]

        self.assertTrue(fast["hd_result_matches_author_rerun"])
        self.assertFalse(fast["per_source_witness_exact"])
        self.assertTrue(fast["global_bound_early_break"])
        self.assertEqual(fast["global_bound_early_break_count"], 409376)
        self.assertEqual(fast["source_count"], 437645)
        self.assertFalse(measured["per_source_witness_exact"])
        self.assertTrue(measured["global_bound_early_break"])
        self.assertEqual(measured["global_bound_early_break_count"], fast["global_bound_early_break_count"])
        self.assertGreater(fast["early_break_fraction"], 0.93)

    def test_goal5347_refinement_does_not_claim_full_reproduction_or_fast_scalar_witnesses(self):
        result = load_json(RESULT)
        refinement = result["goal5347_refinement"]["refined_interpretation"]
        boundary = result["claim_boundary"]

        self.assertTrue(result["goal5347_refinement"]["amends_goal5347_exact_witness_blocker"])
        self.assertTrue(
            refinement[
                "not_a_blocker_for_hd_exec_default_3d_gpu_value_plus_witness_entrypoint_on_existing_level_b_artifacts"
            ]
        )
        self.assertTrue(refinement["still_a_blocker_for_claiming_fast_scalar_route_has_exact_per_source_witnesses"])
        self.assertFalse(boundary["full_xhd_paper_reproduction_claimed"])
        self.assertFalse(boundary["exact_paper_dataset_identity_claimed"])
        self.assertFalse(boundary["author_rt_core_algorithm_equivalence_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["fast_scalar_exact_witness_claimed"])


if __name__ == "__main__":
    unittest.main()
