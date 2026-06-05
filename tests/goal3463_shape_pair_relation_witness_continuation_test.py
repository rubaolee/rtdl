from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "src" / "rtdsl" / "geometry_relation_continuations.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
SCRIPT = ROOT / "scripts" / "goal3463_shape_pair_relation_witness_continuation_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3463_shape_pair_relation_witness_continuation_2026-06-05.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3463_shape_pair_relation_witness_continuation_pod_2026-06-05.json"


class Goal3463ShapePairRelationWitnessContinuationTest(unittest.TestCase):
    def test_module_defines_generic_witness_continuation(self) -> None:
        module = MODULE.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")

        for phrase in (
            "GEOMETRY_RELATION_WITNESS_CUPY_VERSION",
            "ShapePairRelationWitnessCupyResult",
            "shape_pair_relation_witness_cupy",
            "shape_pair_relation_witness_kernel",
            "segment_edge_intersection",
            "left_first_vertex_inside_right",
            "right_first_vertex_inside_left",
            "segment_witness_endpoint_tolerance",
            '"exact_polygon_overlay_area": False',
            '"full_overlay_area_claim_authorized": False',
        ):
            self.assertIn(phrase, module)
        for phrase in (
            "GEOMETRY_RELATION_WITNESS_CUPY_VERSION",
            "ShapePairRelationWitnessCupyResult",
            "shape_pair_relation_witness_cupy",
        ):
            self.assertIn(phrase, init)

    def test_probe_and_report_record_boundaries(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "rtdl.goal3463.shape_pair_relation_witness_continuation.v1",
            "shape_pair_relation_witness_cupy",
            "segment_rows_have_segment_witness",
            "containment_rows_have_containment_witness",
            "unresolved_witness_count",
        ):
            self.assertIn(phrase, script)

        for phrase in (
            "Goal3463",
            "generic CuPy continuation",
            "witness continuation, not an exact polygon overlay-area continuation",
            "Kinds `4` and `5` are failure sentinels",
            "does not authorize exact double-precision geometric claims",
            "does not authorize",
        ):
            self.assertIn(phrase, report)

    @unittest.skipUnless(ARTIFACT.exists(), "Goal3463 pod artifact pending")
    def test_pod_artifact_records_relation_witnesses(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.goal3463.shape_pair_relation_witness_continuation.v1")
        self.assertEqual(payload["goal"], 3463)
        self.assertTrue(payload["all_rows_have_witness"])
        self.assertTrue(payload["segment_rows_have_segment_witness"])
        self.assertTrue(payload["containment_rows_have_containment_witness"])
        self.assertEqual(payload["unresolved_witness_count"], 0)
        self.assertGreater(payload["segment_flag_count"], 0)
        self.assertGreater(payload["containment_flag_count"], 0)
        self.assertEqual(payload["witness_metadata"]["schema"], "rtdl.v2_8.geometry_relation.witness_cupy.v1")
        self.assertIn("1e-5", payload["witness_metadata"]["segment_witness_endpoint_tolerance"])
        self.assertFalse(payload["witness_metadata"]["exact_polygon_overlay_area"])
        self.assertTrue(all(value is False for value in payload["claim_boundary"].values()))


if __name__ == "__main__":
    unittest.main()
