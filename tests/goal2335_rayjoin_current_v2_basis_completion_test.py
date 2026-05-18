from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2335_rayjoin_current_v2_basis_completion_2026-05-18.md"
ARTIFACTS = ROOT / "docs" / "reports" / "goal2335_rayjoin_current_v2_basis_pod"
PATCH = ROOT / "docs" / "research" / "rayjoin_pip_result_export_debug_patch.diff"
SCRIPT = ROOT / "scripts" / "goal2335_rayjoin_pip_vertical_probe_comparison.py"


def _json(name: str) -> dict:
    return json.loads((ARTIFACTS / name).read_text(encoding="utf-8"))


class Goal2335RayJoinCurrentV2BasisCompletionTest(unittest.TestCase):
    def test_pip_result_export_patch_is_diagnostic_and_schema_bound(self) -> None:
        text = PATCH.read_text(encoding="utf-8")
        self.assertIn("RAYJOIN_EXPORT_PIP_RESULTS", text)
        self.assertIn("rtdl.rayjoin.pip_results.v1", text)
        self.assertIn("rayjoin_pip_result_export_debug_patch", text)
        self.assertIn("closest_eid", text)

    def test_current_v2_probe_uses_generic_segment_pair_intersection(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("prepare_segment_pair_intersection_optix", text)
        self.assertIn("pack_segments", text)
        self.assertIn("vertical_probe", text)
        self.assertNotIn("rayjoin-specific native", text.lower())

    def test_pip_same_positive_point_set_matches_at_both_scales(self) -> None:
        expected = {
            4096: (3374, 145295),
            65536: (53372, 2320729),
        }
        for scale, (positive_count, raw_rows) in expected.items():
            with self.subTest(scale=scale):
                payload = _json(f"rtdl_vertical_probe_pip_compare_{scale}.json")
                self.assertEqual(payload["schema"], "rtdl.rayjoin.pip_vertical_probe_comparison.v1")
                self.assertEqual(payload["query_count"], scale)
                self.assertTrue(payload["all_same_positive_point_set"])
                self.assertEqual(payload["runs"][0]["rayjoin_positive_count"], positive_count)
                self.assertEqual(payload["runs"][0]["rtdl_unique_positive_count"], positive_count)
                self.assertEqual(payload["runs"][0]["missing_count"], 0)
                self.assertEqual(payload["runs"][0]["extra_count"], 0)
                self.assertEqual(payload["runs"][0]["raw_intersection_rows"], raw_rows)
                self.assertFalse(payload["claim_boundary"]["rtdl_beats_rayjoin_claim_authorized"])

    def test_report_keeps_release_and_speedup_claims_locked(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("current-v2-correctness-complete-performance-gap-characterized", text)
        self.assertIn("does not have to wait for v3.0", text)
        self.assertIn("does not authorize", text)
        self.assertIn("RTDL beats RayJoin", text)
        self.assertIn("v2.0 release authorization", text)


if __name__ == "__main__":
    unittest.main()
