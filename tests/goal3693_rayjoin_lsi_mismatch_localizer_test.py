from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal3693_rayjoin_lsi_mismatch_localizer_2026-06-07.md"
ARTIFACT_DIR = ROOT / "docs/reports/goal3693_lsi_mismatch_localizer_a5000"
PAIR_DIFF = ARTIFACT_DIR / "lsi_pair_set_diff_summary.json"
GEOMETRY = ARTIFACT_DIR / "missing_pair_geometry.json"
PRECISION = ARTIFACT_DIR / "missing_pair_precision_probe.json"
RAYJOIN_LOG = ARTIFACT_DIR / "rayjoin_lsi_dump.log"
TODO = ROOT / "docs/research/future_version_to_do_list.md"


class Goal3693RayJoinLsiMismatchLocalizerTest(unittest.TestCase):
    def test_pair_set_diff_localizes_exactly_one_missing_pair(self) -> None:
        payload = json.loads(PAIR_DIFF.read_text(encoding="utf-8"))
        normalized = payload["rt_minus1_both"]
        self.assertEqual(normalized["rj_count"], 20860)
        self.assertEqual(normalized["rt_count"], 20859)
        self.assertEqual(normalized["missing_count"], 1)
        self.assertEqual(normalized["extra_count"], 0)
        self.assertEqual(normalized["missing_head"], [[230119, 226567]])

    def test_missing_pair_geometry_is_endpoint_near_hit(self) -> None:
        payload = json.loads(GEOMETRY.read_text(encoding="utf-8"))
        self.assertEqual(payload["missing_pair_rayjoin_zero_based"], [230119, 226567])
        self.assertIn("13654 27 96104 96117 4777 4942", payload["left"]["chain_header"])
        self.assertIn("7277 17 245671 245633 2892 2901", payload["right"]["chain_header"])
        self.assertLess(abs(float(payload["orientations"]["left_a_vs_right"])), 1.0e-7)
        self.assertGreater(float(payload["t"]), 0.0)
        self.assertLess(float(payload["t"]), 1.0e-3)
        self.assertGreater(float(payload["u"]), 0.0)
        self.assertLess(float(payload["u"]), 1.0)

    def test_precision_probe_explains_float_candidate_drop(self) -> None:
        payload = json.loads(PRECISION.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "rtdl.goal3693.lsi_missing_pair_precision_probe.v1")
        self.assertTrue(payload["exact_decimal_predicate"]["hit"])
        self.assertFalse(payload["simulated_float32_device_predicate"]["hit"])
        self.assertEqual(
            payload["simulated_float32_device_predicate"]["drop_reason"],
            "t_below_zero_after_float32_rounding",
        )
        self.assertGreater(float(payload["exact_decimal_predicate"]["t"]), 0.0)
        self.assertLess(float(payload["simulated_float32_device_predicate"]["t"]), 0.0)
        self.assertIn("not RayJoin-specific app logic", payload["diagnosis"])

    def test_report_preserves_generic_boundary_and_next_steps(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("generic segment-pair contract requirement", report)
        self.assertIn("RTDL ids by subtracting one from both sides", report)
        self.assertIn("float32 device-style predicate", report)
        self.assertIn("Bad direction", report)
        self.assertIn("RayJoin-specific exception", report)
        self.assertIn("does not authorize", report)

    def test_rayjoin_log_and_future_todo_capture_context(self) -> None:
        log = RAYJOIN_LOG.read_text(encoding="utf-8")
        self.assertIn("Intersections: 20860", log)
        self.assertIn("queries: 251011", log)
        todo = TODO.read_text(encoding="utf-8")
        self.assertIn("Goal3693", todo)
        self.assertIn("simulated float32 candidate emission", todo)


if __name__ == "__main__":
    unittest.main()
