import json
import math
import statistics
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal4186_contact_native_collect_repeat_accounting_rtx4000ada"
PAYLOAD_PATH = ARTIFACT_DIR / "contact_manifold_optix_grid64_repeat10000.stdout.json"
STDERR_PATH = ARTIFACT_DIR / "contact_manifold_optix_grid64_repeat10000.stderr.txt"
REPORT_PATH = ROOT / "docs" / "reports" / "goal4186_contact_native_collect_repeat_accounting_rtx4000ada_2026-06-09.md"


class Goal4186ContactNativeCollectRepeatAccountingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(PAYLOAD_PATH.read_text(encoding="utf-8"))
        cls.report = REPORT_PATH.read_text(encoding="utf-8")

    def test_repeat_accounting_is_aggregate_and_stable(self) -> None:
        payload = self.payload
        runs = payload["native_collect_runs_sec"]

        self.assertEqual(payload["repeat_count"], 10000)
        self.assertEqual(payload["native_collect_repeat_count"], 10000)
        self.assertEqual(len(runs), 10000)
        self.assertGreater(payload["native_collect_total_sec"], 1.0)
        self.assertTrue(math.isclose(payload["native_collect_total_sec"], sum(runs), rel_tol=1e-12, abs_tol=1e-12))
        self.assertEqual(payload["native_collect_elapsed_sec"], statistics.median(runs))
        self.assertEqual(payload["native_collect_min_sec"], min(runs))
        self.assertEqual(payload["native_collect_max_sec"], max(runs))
        self.assertEqual(
            payload["native_collect_timing_scope"],
            "median_preserves_legacy_field_total_records_repeat_aggregate",
        )

    def test_generic_collect_boundary_and_correctness_remain_intact(self) -> None:
        payload = self.payload

        self.assertTrue(payload["matches_cpu_reference"])
        self.assertEqual(payload["native_generic_symbol"], "rtdl_optix_collect_k_bounded_i64")
        self.assertEqual(payload["primitive_under_test"], "COLLECT_K_BOUNDED")
        self.assertEqual(payload["valid_count"], 64)
        self.assertFalse(payload["overflowed"])
        self.assertFalse(payload["engine_boundary"]["native_collision_logic_allowed"])
        self.assertIn("app-name-free COLLECT_K_BOUNDED", payload["claim_boundary"])
        self.assertNotIn("rtdl_optix_contact", json.dumps(payload).lower())
        self.assertNotIn("rtdl_optix_collision", json.dumps(payload).lower())

    def test_artifact_and_report_do_not_overclaim(self) -> None:
        self.assertEqual(STDERR_PATH.read_text(encoding="utf-8"), "")
        self.assertIn("This is not a new public speedup claim", self.report)
        self.assertIn("measurement hardening", self.report)
        self.assertIn("The native engine remains app-agnostic", self.report)
        self.assertIn("rtdl_optix_collect_k_bounded_i64", self.report)
        self.assertNotIn("release authorized", self.report.lower())
        self.assertNotIn("broad speedup", self.report.lower())


if __name__ == "__main__":
    unittest.main()
