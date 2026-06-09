from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
REPORT = ROOT / "docs" / "reports" / "goal4078_grouped_union_root_path_compression_probe_2026-06-09.md"
SUMMARY = ROOT / "docs" / "reports" / "goal4078_grouped_union_root_path_compression_probe_summary.json"


class Goal4078GroupedUnionRootPathCompressionProbeTest(unittest.TestCase):
    def test_native_grouped_union_path_halving_probe_was_reverted(self) -> None:
        source = CORE.read_text(encoding="utf-8")
        self.assertIn("find_grouped_union_root_readonly", source)
        self.assertNotIn("find_grouped_union_root_compressing", source)
        self.assertNotIn("const int grand = parent[next];", source)

    def test_runtime_metadata_does_not_promote_reverted_policy(self) -> None:
        source = RUNTIME.read_text(encoding="utf-8")
        self.assertNotIn("grouped_union_root_path_compression_policy", source)

    def test_report_records_probe_acceptance_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "Goal4078",
            "generic prepared fixed-radius grouped-union primitive",
            "Decision: `revert_probe_no_material_win`",
            "negative/neutral evidence",
            "does not add native ABI",
            "true-zero-copy",
        ):
            self.assertIn(fragment, text)

    def test_pod_summary_records_revert_decision_without_claims(self) -> None:
        if not SUMMARY.exists():
            self.skipTest("Goal4078 pod summary has not been produced yet")
        import json

        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
        self.assertEqual(payload["goal"], "Goal4078")
        self.assertEqual(payload["decision"], "revert_probe_no_material_win")
        self.assertFalse(payload["claim_boundary"]["release_authorized"])
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["true_zero_copy_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["native_abi_added"])
        for row in payload["rows"]:
            self.assertTrue(row["same_component_size_signature"])


if __name__ == "__main__":
    unittest.main()
