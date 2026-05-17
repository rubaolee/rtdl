import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
REPORT = ROOT / "docs" / "reports" / "goal2301_bounded_closed_shape_point_probe_2026-05-17.md"
BASELINE = ROOT / "docs" / "reports" / "goal2301_bounded_point_probe_baseline_current_pod_2026-05-17.json"
CANDIDATE = ROOT / "docs" / "reports" / "goal2301_bounded_point_probe_candidate_pod_2026-05-17.json"
COUNT_PHASE = ROOT / "docs" / "reports" / "goal2301_bounded_point_probe_candidate_pip_count_phase_pod_2026-05-17.json"
NEGATIVE_SHORT = ROOT / "docs" / "reports" / "goal2301_short_origin_inside_negative_pod_2026-05-17.json"
NEGATIVE_TINY = ROOT / "docs" / "reports" / "goal2301_tiny_crossing_negative_pod_2026-05-17.json"


class Goal2301BoundedClosedShapePointProbeTest(unittest.TestCase):
    def test_kernel_uses_bounded_probe_for_closed_shape_membership(self) -> None:
        text = CORE.read_text(encoding="utf-8")
        start = text.index("extern \"C\" __global__ void __raygen__pip_probe()")
        end = text.index("extern \"C\" __global__ void __miss__pip_miss()", start)
        body = text[start:end]

        self.assertIn("Bounded vertical probe through the point", body)
        self.assertIn("const float query_half_extent = 0.5f", body)
        self.assertIn("make_float3(px, py - query_half_extent, 0.0f)", body)
        self.assertIn("2.0f * query_half_extent", body)
        self.assertNotIn("1.0e30f", body)

    def test_pod_artifacts_preserve_exact_count_and_improve_pip(self) -> None:
        baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
        candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))

        self.assertTrue(baseline["pip"]["matches_prior_expected_count"])
        self.assertTrue(candidate["pip"]["matches_prior_expected_count"])
        self.assertEqual(candidate["pip"]["positive_rows"]["values"], [8686] * 7)
        self.assertEqual(candidate["pip"]["scalar_count"]["values"], [8686] * 7)

        baseline_rows = baseline["pip"]["positive_rows"]["median_sec"]
        candidate_rows = candidate["pip"]["positive_rows"]["median_sec"]
        baseline_count = baseline["pip"]["scalar_count"]["median_sec"]
        candidate_count = candidate["pip"]["scalar_count"]["median_sec"]

        self.assertGreater(baseline_rows / candidate_rows, 2.0)
        self.assertGreater(baseline_count / candidate_count, 4.0)

    def test_phase_artifact_records_candidate_write_drop(self) -> None:
        phase = json.loads(COUNT_PHASE.read_text(encoding="utf-8"))
        self.assertTrue(phase["matches_expected"])
        self.assertEqual(phase["values"], [8686] * 7)
        median_candidate_write = sorted(
            sample["candidate_write_pass"] for sample in phase["phases"]
        )[len(phase["phases"]) // 2]
        self.assertLess(median_candidate_write, 0.004)

    def test_rejected_tiny_probe_variants_are_documented(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Rejected Variants", report)
        self.assertIn("returned zero PIP positives", report)

        short = json.loads(NEGATIVE_SHORT.read_text(encoding="utf-8"))
        tiny = json.loads(NEGATIVE_TINY.read_text(encoding="utf-8"))
        self.assertEqual(short["pip"]["scalar_count"]["values"], [0] * 7)
        self.assertEqual(tiny["values"], [0] * 7)

    def test_report_keeps_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("No RayJoin paper reproduction", text)
        self.assertIn("No claim that RTDL beats RayJoin", text)
        self.assertIn("No true zero-copy claim", text)
        self.assertIn("No v2.0 release authorization", text)
        self.assertIsNotNone(re.search(r"\bclosed-shape membership\b", text))


if __name__ == "__main__":
    unittest.main()
