from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTINUATIONS = ROOT / "src" / "rtdsl" / "geometry_relation_continuations.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
SCRIPT = ROOT / "scripts" / "goal3467_shape_pair_relation_complexity_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3467_shape_pair_relation_complexity_probe_2026-06-05.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3467_shape_pair_relation_complexity_probe_pod_2026-06-05.json"


class Goal3467ShapePairRelationComplexityProbeTest(unittest.TestCase):
    def test_runtime_adds_generic_complexity_continuation(self) -> None:
        text = CONTINUATIONS.read_text(encoding="utf-8")

        for phrase in (
            "GEOMETRY_RELATION_COMPLEXITY_CUPY_VERSION",
            "shape_pair_relation_convexity_kernel",
            "ShapePairRelationComplexityCupyResult",
            "shape_pair_relation_complexity_cupy",
            "general_overlay_required",
            "not an exact overlay-area computation",
            "app_specific_engine_logic_allowed",
            "full_overlay_area_claim_authorized",
        ):
            self.assertIn(phrase, text)

    def test_exports_complexity_continuation(self) -> None:
        text = INIT.read_text(encoding="utf-8")

        for phrase in (
            "GEOMETRY_RELATION_COMPLEXITY_CUPY_VERSION",
            "ShapePairRelationComplexityCupyResult",
            "shape_pair_relation_complexity_cupy",
        ):
            self.assertIn(phrase, text)

    def test_probe_records_complexity_and_claim_boundary(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "rtdl.goal3467.shape_pair_relation_complexity_probe.v1",
            "shape_pair_relation_complexity_cupy",
            "simple_clip_sufficient_for_all_rows",
            "general_overlay_required_row_counts",
            "claim_boundary",
        ):
            self.assertIn(phrase, script)

        for phrase in (
            "generic CuPy relation-stream complexity classifier",
            "not an exact overlay-area primitive",
            "simple convex clipping continuation",
            "simple-polygon overlay path",
            "full exact overlay-area completion claims",
        ):
            self.assertIn(phrase, report)

    @unittest.skipUnless(ARTIFACT.exists(), "Goal3467 pod artifact pending")
    def test_pod_artifact_records_public_cdb_complexity(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.goal3467.shape_pair_relation_complexity_probe.v1")
        self.assertEqual(payload["goal"], 3467)
        self.assertEqual(payload["iterations"], 4)
        self.assertTrue(payload["all_row_counts_stable"])
        self.assertTrue(payload["all_general_overlay_counts_stable"])
        self.assertGreater(payload["row_counts"][0], 0)
        self.assertGreater(payload["general_overlay_required_row_counts"][0], 0)
        self.assertFalse(payload["simple_clip_sufficient_for_all_rows"])
        self.assertTrue(all(value is False for value in payload["claim_boundary"].values()))


if __name__ == "__main__":
    unittest.main()
