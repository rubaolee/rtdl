from __future__ import annotations

from pathlib import Path
import json
import unittest

import rtdsl as rt
from examples.benchmark_apps.rtnn import rtdl_rtnn_benchmark_app as rtnn_app


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4308_rtnn_embree_front_door_for_v2_11_packet_2026-06-11.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal4308_rtnn_embree_front_door_local_linux.json"


class Goal4308RtnnEmbreeFrontDoorTest(unittest.TestCase):
    def test_rtnn_registry_row_is_embree_not_numba_exception(self) -> None:
        rows = {row["app"]: row for row in rt.current_embree_cpu_partner_reference_rows()}
        row = rows["rtnn"]
        self.assertEqual(row["row_id"], "rtnn_embree_cpu_ann_candidate_quality_reference")
        self.assertEqual(row["route_class"], "embree_cpu_rt_plus_python_continuation")
        self.assertTrue(row["uses_embree"])
        self.assertFalse(row["uses_numba"])
        self.assertIn("ann_embree_quality", row["command"])
        validation = rt.validate_current_embree_cpu_partner_reference()
        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["errors"], ())

    def test_rtnn_embree_mode_keeps_boundary_precise(self) -> None:
        payload = rtnn_app.ann_embree_quality_payload(copies=1)
        self.assertEqual(payload["app"], "rtnn_neighbor_search")
        self.assertEqual(payload["mode"], "ann_embree_quality")
        self.assertEqual(payload["backend"], "embree")
        self.assertTrue(payload["uses_embree"])
        self.assertFalse(payload["uses_numba"])
        self.assertIn("rt_path_note", payload)
        self.assertNotIn("optix_performance", payload)
        self.assertTrue(payload["inherited_ann_optix_performance_note_present"])
        self.assertFalse(payload["claim_boundary"]["native_engine_customization"])
        self.assertFalse(payload["claim_boundary"]["paper_reproduction_claim_authorized"])
        self.assertIn("not the 3-D RTNN ranked-summary path", payload["boundary"])

    def test_report_and_artifact_record_linux_row(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal4308",
            "rtnn_embree_cpu_ann_candidate_quality_reference",
            "ann_embree_quality",
            "not the 3-D RTNN ranked-summary path",
            "does not authorize",
        ):
            self.assertIn(phrase, text)

        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertTrue(artifact["all_pass"])
        self.assertEqual(artifact["validation"]["status"], "accept")
        self.assertEqual(artifact["validation"]["errors"], [])
        row = artifact["rows"][0]
        self.assertEqual(row["row_id"], "rtnn_embree_cpu_ann_candidate_quality_reference")
        self.assertTrue(row["uses_embree"])
        self.assertFalse(row["uses_numba"])
        self.assertEqual(row["status"], "pass")
        stdout_payload = json.loads(row["stdout_tail"])
        self.assertIn("rt_path_note", stdout_payload)
        self.assertNotIn("optix_performance", stdout_payload)


if __name__ == "__main__":
    unittest.main()
