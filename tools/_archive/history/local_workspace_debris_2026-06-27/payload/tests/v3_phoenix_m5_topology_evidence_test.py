import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "rebuild" / "v3" / "evidence" / "phoenix_v3_m5_topology_20260620"


class V3PhoenixM5TopologyEvidenceTest(unittest.TestCase):
    def load(self, rel: str):
        return json.loads((EVIDENCE / rel).read_text(encoding="utf-8"))

    def test_intake_passes_with_author_code_but_keeps_release_blocked(self):
        payload = self.load("m5_topology_intake_summary.json")
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["overall_status"], "internal_evidence_with_author_code")
        self.assertEqual(payload["status_label"], "internal-author-complete")
        self.assertEqual(payload["generic_capability"], "point_location_topology_stream")
        self.assertEqual(payload["m5_author_code_comparison_status"], "complete")
        self.assertEqual(payload["overlay_author_comparison_status"], "not_applicable_internal_same_contract_only")
        self.assertEqual(payload["query_exec_status"], "present")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertEqual(payload["phoenix_m7_qualified_release_rows"], 0)
        self.assertEqual(payload["failures"], [])
        self.assertTrue(payload["checks"]["optix_hardware_gate_passed"])
        self.assertTrue(payload["checks"]["pip_same_contract_ready"])
        self.assertTrue(payload["checks"]["overlay_same_contract_ready"])

    def test_pip_uses_filtered_safe_stream_and_matches_exact_rows(self):
        payload = self.load("m5_pip_point_location_parity_filtered_100k/summary.json")
        protocol = payload["protocol"]
        self.assertEqual(protocol["artifact_methodology_label"], "parity_filtered_100k")
        self.assertTrue(protocol["legacy_safe100k_name_retired"])
        self.assertTrue(protocol["parity_filter_requested"])
        self.assertEqual(protocol["query_generation"], "backend_parity_filtered_random_bbox")
        self.assertFalse(protocol["row_materialization_in_timed_path"])
        self.assertEqual(protocol["optix_repeats"], 1000)
        self.assertEqual(protocol["embree_repeats"], 1000)
        parity_filter = payload["parity_filter"]
        self.assertEqual(parity_filter["status"], "pass")
        self.assertEqual(parity_filter["accepted_count"], 100000)
        self.assertEqual(parity_filter["rejected_count"], 1)
        correctness = payload["correctness_sample"]
        self.assertEqual(correctness["sample_count"], 100000)
        self.assertEqual(correctness["mismatch_count_first_10_materialized"], 0)
        self.assertEqual(payload["rtdl"]["optix"]["positive_face_count"], payload["rtdl"]["embree"]["positive_face_count"])
        self.assertGreater(payload["comparison"]["rtdl_optix_speedup_vs_rtdl_embree"], 1.0)
        self.assertIsNotNone(payload["rayjoin_rt"])
        self.assertGreater(payload["comparison"]["rayjoin_rt_speedup_vs_rtdl_optix"], 1.0)
        self.assertGreater(payload["comparison"]["rayjoin_rt_speedup_vs_rtdl_optix_native_traversal"], 1.0)
        self.assertIn("timing_basis_note", payload["comparison_methodology"])
        self.assertLess(payload["rayjoin_rt"]["query_ms"], payload["rtdl"]["optix"]["hot_median_sec"] * 1000.0)

    def test_overlay_same_contract_internal_only(self):
        payload = self.load("m5_overlay_active_count_same_contract.json")
        comparison = payload["comparison"]
        self.assertTrue(comparison["same_output_contract"])
        self.assertTrue(comparison["active_counts_match"])
        self.assertTrue(comparison["all_row_materialization_avoided"])
        self.assertEqual(comparison["active_count"], 174)
        self.assertGreater(comparison["embree_over_optix_timed_median"], 1.0)
        self.assertFalse(comparison["public_speedup_claim_authorized"])
        self.assertFalse(comparison["rt_core_speedup_claim_authorized"])
        rows = {row["backend"]: row for row in payload["rows"]}
        self.assertEqual(set(rows), {"embree", "optix"})
        self.assertEqual(rows["optix"]["output_contract"], "overlay_active_pair_dependency_count")
        self.assertEqual(rows["embree"]["output_contract"], "overlay_active_pair_dependency_count")

    def test_artifact_has_source_and_hardware_provenance(self):
        hardware = self.load("optix_hardware_gate.json")
        self.assertEqual(hardware["status"], "pass")
        self.assertTrue(hardware["checks"]["rt_hardware_name_present"])
        self.assertTrue((EVIDENCE / "source_manifest.sha256").exists())
        manifest = (EVIDENCE / "source_manifest.sha256").read_text(encoding="utf-8")
        self.assertIn("scripts/goal4373_rayjoin_cdb_point_location_compare.py", manifest)
        self.assertIn("scripts/v3_phoenix_m5_topology_intake.py", manifest)
        note = EVIDENCE / "m5_pip_point_location_parity_filtered_100k" / "METHODOLOGY_NOTE.md"
        self.assertIn("`safe100k` name is retired", note.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
