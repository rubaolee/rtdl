from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3420_device_predicate_page_equivalence_probe_2026-06-04.json"
REPORT = ROOT / "docs" / "reports" / "goal3420_device_predicate_page_equivalence_2026-06-04.md"
SCRIPT = ROOT / "scripts" / "goal3420_device_predicate_page_equivalence_probe.py"


class Goal3420DevicePredicatePageEquivalenceTest(unittest.TestCase):
    def test_probe_uses_device_predicate_columns_not_host_refined_exact_bridge(self):
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("prepared.candidate_device_columns", script)
        self.assertIn("host_exact_used_only_as_oracle", script)
        self.assertIn("host_refinement_used_to_produce_device_columns", script)
        self.assertIn('"universal_device_exact_claim_authorized": False', script)
        self.assertIn("pair_multiset_match_host_exact", script)
        self.assertNotIn("prepared.exact_device_columns(", script)
        self.assertNotIn("exact_device_columns_native_page_plan", script)

    def test_report_keeps_device_exact_boundary_honest(self):
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("host-refined", report)
        self.assertIn("host-exact path is used as a correctness oracle", report)
        self.assertIn("not the final v2.8", report)
        self.assertIn("Universal exact predicate", report)
        self.assertIn("release claims remain blocked", report)

    @unittest.skipUnless(ARTIFACT.exists(), "Goal3420 pod artifact pending")
    def test_pod_artifact_records_full_cdb_device_predicate_equivalence(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.goal3420.device_predicate_page_equivalence_probe.v1")
        self.assertEqual(payload["goal"], 3420)
        self.assertTrue(payload["rtdl_commit"])
        self.assertIn("NVIDIA", payload["gpu"])
        self.assertEqual(payload["point_count"], 16545)
        self.assertEqual(payload["shape_count"], 15700)

        contract = payload["contract"]
        self.assertEqual(contract["schema"], "rtdl.pair_column_paged_recovery.v1")
        self.assertEqual(contract["page_size"], 2048)
        self.assertEqual(contract["initial_capacity"], 100)
        self.assertEqual(contract["overflow_policy"], "fail_closed_explicit_retry")
        self.assertFalse(contract["automatic_retry_authorized"])
        self.assertFalse(contract["hidden_dispatch_authorized"])

        recovery = payload["recovery_summary"]
        self.assertEqual(recovery["page_count"], 9)
        self.assertEqual(recovery["overflow_page_count"], 9)
        self.assertEqual(recovery["retry_page_count"], 9)
        self.assertEqual(recovery["grouped_source_row_count"], payload["device_predicate_pair_count"])
        self.assertEqual(recovery["merge_rule"], "key_addition")

        self.assertEqual(payload["host_exact_pair_count"], 47262)
        self.assertEqual(payload["device_predicate_pair_count"], 47262)
        self.assertTrue(payload["pair_multiset_match_host_exact"])
        self.assertEqual(payload["pair_missing_from_device_sample"], [])
        self.assertEqual(payload["pair_extra_on_device_sample"], [])
        self.assertTrue(payload["group_counts_match_host"])
        self.assertEqual(payload["missing_group_key_count"], 0)
        self.assertEqual(payload["extra_group_key_count"], 0)
        self.assertEqual(payload["mismatched_group_value_count"], 0)

        boundary = payload["device_predicate_boundary"]
        self.assertTrue(boundary["device_predicate_columns_produced"])
        self.assertFalse(boundary["host_refinement_used_to_produce_device_columns"])
        self.assertTrue(boundary["host_exact_used_only_as_oracle"])
        self.assertTrue(boundary["device_predicate_matches_host_exact_on_this_dataset"])
        self.assertFalse(boundary["universal_exact_predicate_claim_authorized"])
        self.assertFalse(boundary["native_page_plan_handle_used"])
        self.assertFalse(boundary["automatic_retry_authorized"])
        self.assertFalse(boundary["hidden_dispatch_authorized"])

        for key, value in payload["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
