from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt
from rtdsl import generic_primitives as gp


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal2950_raydb_payload_grouped_sum_front_door_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal2950_raydb_payload_grouped_sum_front_door_probe_2026-06-01.md"
POD_ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2950_raydb_payload_grouped_sum_front_door_probe_pod"
    / "goal2950_raydb_payload_grouped_sum_front_door_probe.json"
)


class Goal2950RaydbPayloadGroupedSumFrontDoorProbeTest(unittest.TestCase):
    def test_packed_inputs_are_preserved_by_front_door_normalizers(self) -> None:
        rays = rt.pack_rays_3d_from_arrays(
            (0,),
            (0.0,),
            (0.0,),
            (-1.0,),
            (0.0,),
            (0.0,),
            (1.0,),
            (2.0,),
        )
        triangles = rt.pack_triangles_3d_from_arrays(
            (0,),
            (0.0,),
            (0.0,),
            (0.0,),
            (1.0,),
            (0.0,),
            (0.0,),
            (0.0,),
            (1.0,),
            (0.0,),
        )

        self.assertIs(gp._normalize_ray3d_input_for_front_door(rays), rays)
        self.assertIs(gp._normalize_triangle3d_input_for_front_door(triangles), triangles)
        self.assertEqual(1, gp._front_door_record_count(rays))
        self.assertEqual(1, gp._front_door_record_count(triangles))

    def test_runner_uses_payload_front_door_and_keeps_claim_boundary(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("prepare_generic_ray_triangle_event_ordered_payload_grouped_sum_3d", source)
        self.assertIn('partner="cupy"', source)
        self.assertIn("deduplicate_primitives=True", source)
        self.assertIn("PAPER_RT_OPTIX_V2_5_PRIMITIVE_FIRST_BACKEND", source)
        self.assertIn('"public_speedup_claim_authorized": False', source)
        self.assertIn('"native_engine_customization": False', source)

    def test_report_records_diagnostic_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal2950", text)
        self.assertIn("preserves packed RTDL ray and", text)
        self.assertIn("primitive-first fused grouped reduction is still", text)
        self.assertIn("expected to win", text)
        self.assertIn("not a v2.5 release authorization", text)
        self.assertIn("RayDB paper reproduction claim", text)

    def test_pod_artifact_when_available(self) -> None:
        if not POD_ARTIFACT.exists():
            self.skipTest("Goal2950 pod artifact has not been imported yet")
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual("pass", payload["status"])
        self.assertEqual([], payload["source_dirty"])
        self.assertEqual([250000, 1000000], payload["row_counts"])
        self.assertEqual(["count", "sum"], payload["modes"])
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["true_zero_copy_authorized"])
        for case in payload["cases"]:
            self.assertEqual("pass", case["status"])
            self.assertTrue(case["matches_cpu_reference"])
            self.assertTrue(case["deduplicate_primitives"])
            self.assertIsNotNone(case["primitive_first_comparison"])
            self.assertIsNotNone(case["payload_front_door_vs_primitive_first_ratio"])


if __name__ == "__main__":
    unittest.main()
