from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTINUATIONS = ROOT / "src" / "rtdsl" / "geometry_relation_continuations.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
SCRIPT = ROOT / "scripts" / "goal3471_convex_overlay_area_fast_path_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3471_convex_overlay_area_fast_path_probe_2026-06-05.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3471_convex_overlay_area_fast_path_probe_pod_2026-06-05.json"


class Goal3471ConvexOverlayAreaFastPathProbeTest(unittest.TestCase):
    def test_runtime_adds_convex_overlay_fast_path(self) -> None:
        text = CONTINUATIONS.read_text(encoding="utf-8")

        for phrase in (
            "GEOMETRY_RELATION_CONVEX_OVERLAY_AREA_CUPY_VERSION",
            "shape_pair_relation_convex_overlay_area_kernel",
            "ShapePairConvexOverlayAreaCupyResult",
            "shape_pair_relation_convex_overlay_area_cupy",
            "exact_area_for_supported_convex_rows_only",
            "unsupported_nonconvex",
            "full_exact_overlay_area_completed",
        ):
            self.assertIn(phrase, text)

    def test_exports_convex_overlay_fast_path(self) -> None:
        text = INIT.read_text(encoding="utf-8")

        for phrase in (
            "GEOMETRY_RELATION_CONVEX_OVERLAY_AREA_CUPY_VERSION",
            "ShapePairConvexOverlayAreaCupyResult",
            "shape_pair_relation_convex_overlay_area_cupy",
        ):
            self.assertIn(phrase, text)

    def test_probe_and_report_keep_boundary(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "rtdl.goal3471.convex_overlay_area_fast_path_probe.v1",
            "synthetic_convex_fixture",
            "shape_pair_relation_convex_overlay_area_cupy",
            "all_supported_counts_stable",
            "claim_boundary",
        ):
            self.assertIn(phrase, script)

        for phrase in (
            "Convex Overlay-Area Fast-Path Probe",
            "exact only for supported convex rows",
            "unsupported nonconvex row",
            "does not close the",
            "full exact overlay-area completion claims",
        ):
            self.assertIn(phrase, report)

    @unittest.skipUnless(ARTIFACT.exists(), "Goal3471 pod artifact pending")
    def test_pod_artifact_records_convex_subset(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.goal3471.convex_overlay_area_fast_path_probe.v1")
        self.assertEqual(payload["goal"], 3471)
        self.assertTrue(payload["synthetic_convex_fixture"]["passed"])
        self.assertEqual(payload["synthetic_convex_fixture"]["status"][0], 0)
        self.assertEqual(payload["synthetic_convex_fixture"]["status"][1], 1)
        public = payload["public_cdb"]
        self.assertTrue(public["all_supported_counts_stable"])
        self.assertTrue(public["all_status_counts_stable"])
        self.assertGreater(public["supported_row_counts"][0], 0)
        self.assertGreater(public["status_counts"][0].get("1", 0), 0)
        self.assertTrue(all(value is False for value in payload["claim_boundary"].values()))


if __name__ == "__main__":
    unittest.main()
