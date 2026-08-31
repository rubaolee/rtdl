from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3421_cupy_refined_device_predicate_page_probe_2026-06-04.json"
REPORT = ROOT / "docs" / "reports" / "goal3421_cupy_refined_device_predicate_page_probe_2026-06-04.md"
SCRIPT = ROOT / "scripts" / "goal3421_cupy_refined_device_predicate_page_probe.py"
CLOSED_SHAPE_TOPOLOGY = ROOT / "src" / "rtdsl" / "closed_shape_topology.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"


class Goal3421CuPyRefinedDevicePredicatePageProbeTest(unittest.TestCase):
    def test_reusable_cupy_refinement_helper_is_exported_and_bounded(self):
        source = CLOSED_SHAPE_TOPOLOGY.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")

        self.assertIn("def refine_closed_shape_membership_candidate_columns_exact_cupy", source)
        self.assertIn("exact_closed_shape_candidate_refine", source)
        self.assertIn("point_eps", source)
        self.assertIn("host_refined_rows_materialized", source)
        self.assertIn('"native_exact_device_row_stream_produced": False', source)
        self.assertIn("refine_closed_shape_membership_candidate_columns_exact_cupy", init)

    def test_probe_uses_rt_candidate_then_cupy_refinement(self):
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("prepared.candidate_device_columns", script)
        self.assertIn("refine_closed_shape_membership_candidate_columns_exact_cupy", script)
        self.assertIn("host_exact_used_only_as_oracle", script)
        self.assertIn("--point-eps", script)
        self.assertIn('"native_exact_device_predicate_claim_authorized": False', script)
        self.assertNotIn("prepared.exact_device_columns(", script)
        self.assertNotIn("exact_device_columns_native_page_plan", script)

    def test_report_keeps_native_boundary_clear(self):
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("308 extra pairs", report)
        self.assertIn("partner-layer evidence", report)
        self.assertIn("not the final native v2.8", report)
        self.assertIn("Host exact rows are used only as a correctness oracle", report)
        self.assertIn("claims remain blocked", report)

    @unittest.skipUnless(ARTIFACT.exists(), "Goal3421 pod artifact pending")
    def test_pod_artifact_records_full_cdb_refinement_gap(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.goal3421.cupy_refined_device_predicate_page_probe.v1")
        self.assertEqual(payload["goal"], 3421)
        self.assertTrue(payload["rtdl_commit"])
        self.assertIn("NVIDIA", payload["gpu"])
        self.assertEqual(payload["point_count"], 16545)
        self.assertEqual(payload["shape_count"], 15700)

        self.assertEqual(payload["host_exact_pair_count"], 47262)
        self.assertEqual(payload["rt_candidate_pair_count"], 47570)
        self.assertEqual(payload["cupy_refined_pair_count"], 47045)
        self.assertEqual(payload["dropped_candidate_pair_count"], 525)
        self.assertEqual(payload["point_eps"], 1e-9)
        self.assertFalse(payload["pair_multiset_match_host_exact"])
        self.assertGreater(len(payload["pair_missing_from_refined_sample"]), 0)
        self.assertEqual(payload["pair_extra_on_refined_sample"], [])
        self.assertFalse(payload["group_counts_match_host"])
        self.assertEqual(payload["missing_group_key_count"], 0)
        self.assertEqual(payload["extra_group_key_count"], 0)
        self.assertEqual(payload["mismatched_group_value_count"], 97)

        boundary = payload["refinement_boundary"]
        self.assertTrue(boundary["rt_candidate_columns_produced"])
        self.assertTrue(boundary["cupy_device_refinement_used"])
        self.assertFalse(boundary["host_refinement_used_to_produce_refined_columns"])
        self.assertTrue(boundary["host_exact_used_only_as_oracle"])
        self.assertFalse(boundary["refined_columns_match_host_exact_on_this_dataset"])
        self.assertFalse(boundary["native_exact_device_predicate_implemented"])
        self.assertFalse(boundary["native_page_plan_handle_used"])

        for key, value in payload["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
